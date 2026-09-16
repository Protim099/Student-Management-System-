requireAuth();

let currentPage = 1;
let currentQuery = '';
let editingId = null;

const tableBody = document.getElementById('studentTableBody');
const emptyMsg = document.getElementById('emptyMsg');
const pagination = document.getElementById('pagination');
const modal = document.getElementById('studentModal');
const form = document.getElementById('studentForm');
const modalTitle = document.getElementById('modalTitle');
const formError = document.getElementById('formError');

// ---- User info ----
const user = getUser();
if (user) {
  document.getElementById('userLabel').textContent = `👋 ${user.username} (${user.role})`;
}

document.getElementById('logoutBtn').addEventListener('click', () => {
  clearAuth();
  window.location.href = 'index.html';
});

// ---- Load stats ----
async function loadStats() {
  try {
    const data = await fetchStats();
    document.getElementById('statTotal').textContent = data.total_students;
    const deptEl = document.getElementById('statDept');
    deptEl.innerHTML = data.by_department.map(d =>
      `<span class="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full">${d.department}: ${d.count}</span>`
    ).join('') || '<span class="text-gray-400">কোনো ডেটা নেই</span>';
  } catch (err) {
    console.error(err);
  }
}

// ---- Load students table ----
async function loadStudents() {
  try {
    const data = await fetchStudents(currentQuery, currentPage);
    tableBody.innerHTML = '';

    if (data.students.length === 0) {
      emptyMsg.classList.remove('hidden');
    } else {
      emptyMsg.classList.add('hidden');
    }

    data.students.forEach(s => {
      const tr = document.createElement('tr');
      tr.className = 'hover:bg-gray-50';
      tr.innerHTML = `
        <td class="px-4 py-3 font-medium text-gray-700">${escapeHtml(s.roll)}</td>
        <td class="px-4 py-3">${escapeHtml(s.name)}</td>
        <td class="px-4 py-3">${escapeHtml(s.department || '-')}</td>
        <td class="px-4 py-3">${escapeHtml(s.semester || '-')}</td>
        <td class="px-4 py-3">${escapeHtml(s.email || '-')}</td>
        <td class="px-4 py-3">${escapeHtml(s.phone || '-')}</td>
        <td class="px-4 py-3 text-right space-x-2">
          <button data-id="${s.id}" class="editBtn text-indigo-600 hover:underline text-sm">Edit</button>
          <button data-id="${s.id}" class="deleteBtn text-red-500 hover:underline text-sm">Delete</button>
        </td>
      `;
      tableBody.appendChild(tr);
    });

    renderPagination(data.page, data.pages);
    attachRowActions();
  } catch (err) {
    console.error(err);
  }
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function renderPagination(page, pages) {
  pagination.innerHTML = '';
  if (pages <= 1) return;

  for (let i = 1; i <= pages; i++) {
    const btn = document.createElement('button');
    btn.textContent = i;
    btn.className = `px-3 py-1 rounded-lg text-sm ${i === page ? 'bg-indigo-600 text-white' : 'bg-white border border-gray-300 text-gray-600 hover:bg-gray-50'}`;
    btn.addEventListener('click', () => {
      currentPage = i;
      loadStudents();
    });
    pagination.appendChild(btn);
  }
}

function attachRowActions() {
  document.querySelectorAll('.editBtn').forEach(btn => {
    btn.addEventListener('click', () => openEditModal(btn.dataset.id));
  });
  document.querySelectorAll('.deleteBtn').forEach(btn => {
    btn.addEventListener('click', () => handleDelete(btn.dataset.id));
  });
}

// ---- Search ----
let searchTimeout;
document.getElementById('searchInput').addEventListener('input', (e) => {
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    currentQuery = e.target.value.trim();
    currentPage = 1;
    loadStudents();
  }, 350);
});

// ---- Modal open/close ----
function openAddModal() {
  editingId = null;
  modalTitle.textContent = 'নতুন স্টুডেন্ট যোগ করুন';
  form.reset();
  formError.classList.add('hidden');
  modal.classList.remove('hidden');
  modal.classList.add('flex');
}

async function openEditModal(id) {
  try {
    const student = await apiRequest(`/students/${id}`);
    editingId = id;
    modalTitle.textContent = 'স্টুডেন্ট তথ্য এডিট করুন';
    document.getElementById('name').value = student.name || '';
    document.getElementById('roll').value = student.roll || '';
    document.getElementById('email').value = student.email || '';
    document.getElementById('phone').value = student.phone || '';
    document.getElementById('department').value = student.department || '';
    document.getElementById('semester').value = student.semester || '';
    document.getElementById('address').value = student.address || '';
    formError.classList.add('hidden');
    modal.classList.remove('hidden');
    modal.classList.add('flex');
  } catch (err) {
    alert(err.message || 'তথ্য লোড করা যায়নি');
  }
}

function closeModal() {
  modal.classList.add('hidden');
  modal.classList.remove('flex');
}

document.getElementById('addStudentBtn').addEventListener('click', openAddModal);
document.getElementById('cancelBtn').addEventListener('click', closeModal);

// ---- Form submit (create / update) ----
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById('name').value.trim(),
    roll: document.getElementById('roll').value.trim(),
    email: document.getElementById('email').value.trim(),
    phone: document.getElementById('phone').value.trim(),
    department: document.getElementById('department').value.trim(),
    semester: document.getElementById('semester').value.trim(),
    address: document.getElementById('address').value.trim(),
  };

  try {
    if (editingId) {
      await updateStudent(editingId, payload);
    } else {
      await createStudent(payload);
    }
    closeModal();
    loadStudents();
    loadStats();
  } catch (err) {
    formError.textContent = err.message || 'সংরক্ষণ করা যায়নি';
    formError.classList.remove('hidden');
  }
});

// ---- Delete ----
async function handleDelete(id) {
  if (!confirm('আপনি কি নিশ্চিত এই স্টুডেন্টকে ডিলিট করতে চান?')) return;
  try {
    await deleteStudent(id);
    loadStudents();
    loadStats();
  } catch (err) {
    alert(err.message || 'ডিলিট করা যায়নি');
  }
}

// ---- Init ----
loadStats();
loadStudents();
