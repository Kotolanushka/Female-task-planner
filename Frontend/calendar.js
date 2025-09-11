if (window.NodeList && !NodeList.prototype.forEach) {
  NodeList.prototype.forEach = Array.prototype.forEach;
}

const phaseColors = {
  menstruation: 'menstruation',
  follicular: 'follicular',
  ovulation: 'ovulation',
  luteal: 'luteal'
};

const monthsRu = [
  translator.gettext('Январь'),
  translator.gettext('Февраль'),
  translator.gettext('Март'),
  translator.gettext('Апрель'),
  translator.gettext('Май'),
  translator.gettext('Июнь'),
  translator.gettext('Июль'),
  translator.gettext('Август'),
  translator.gettext('Сентябрь'),
  translator.gettext('Октябрь'),
  translator.gettext('Ноябрь'),
  translator.gettext('Декабрь')
];

let currentMonth;
let currentYear;
let selectedTaskIndex = null;
let selectedDate = null;
let moveToDate = null;

function normalizeDate(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

// ====================== TASKS ==========================
async function saveTask(date, taskText, phase = null) {
  const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  try {
    let tasksStore = JSON.parse(localStorage.getItem('tasks') || '{}');
    if (!tasksStore[key]) tasksStore[key] = [];

    if (!phase) {
      const startVal = localStorage.getItem('start_date') || document.getElementById('start_date')?.value;
      const periodVal = parseInt(localStorage.getItem('period') || document.getElementById('period')?.value || '28');
      const startDate = startVal ? new Date(startVal) : null;
      if (startDate && !isNaN(periodVal)) {
        const pf = getPhaseInfo(date, startDate, periodVal);
        phase = pf.phase;
      } else {
        phase = 'unknown';
      }
    }

    let adviceText = '';
    try {
      const resp = await fetch('http://127.0.0.1:8000/advice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: taskText, phase: phase, locale: 'ru' })
      });
      if (resp.ok) {
        const json = await resp.json();
        adviceText = json.suggestion || json.reason || '';
        console.log('AI совет получен:', json);
      } else {
        console.warn('API вернул ошибку:', resp.status, resp.statusText);
        adviceText = 'Совет недоступен (API ошибка)';
      }
    } catch (err) {
      console.error('Ошибка при запросе совета:', err);
      adviceText = 'Совет недоступен (нет соединения)';
    }

    tasksStore[key].push({ text: taskText, advice: adviceText });
    localStorage.setItem('tasks', JSON.stringify(tasksStore));

    console.log(`Задача сохранена: ${taskText} (совет: ${adviceText})`);
  } catch (e) {
    console.error('Failed to save task:', e);
    alert('Error saving task.');
  }
}

function getTasks(date) {
  const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  try {
    const tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
    return tasks[key] || [];
  } catch (e) {
    console.error('Failed to get tasks:', e);
    return [];
  }
}

function deleteTask(date, taskIndex) {
  const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  let tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
  if (tasks[key] && tasks[key].length > taskIndex) {
    tasks[key].splice(taskIndex, 1);
    if (tasks[key].length === 0) delete tasks[key];
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }
}

function moveTask(fromDate, toDate, taskIndex) {
  const fromKey = `${fromDate.getFullYear()}-${fromDate.getMonth()}-${fromDate.getDate()}`;
  const toKey = `${toDate.getFullYear()}-${toDate.getMonth()}-${toDate.getDate()}`;
  let tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
  if (tasks[fromKey] && tasks[fromKey].length > taskIndex) {
    const task = tasks[fromKey][taskIndex];
    tasks[fromKey].splice(taskIndex, 1);
    if (tasks[fromKey].length === 0) delete tasks[fromKey];
    if (!tasks[toKey]) tasks[toKey] = [];
    tasks[toKey].push(task);
    localStorage.setItem('tasks', JSON.stringify(tasks));
  }
}

function changeMonth(offset) {
  currentMonth += offset;
  if (currentMonth < 0) {
    currentMonth = 11;
    currentYear--;
  } else if (currentMonth > 11) {
    currentMonth = 0;
    currentYear++;
  }
  generateCalendar(currentMonth, currentYear);
  updateCalendarWithPhases();
}

// ====================== CALENDAR ==========================
document.addEventListener('DOMContentLoaded', () => {
  const now = new Date();
  currentMonth = now.getMonth();
  currentYear = now.getFullYear();

  document.getElementById('start_date').value = localStorage.getItem('start_date') || null;
  document.getElementById('period').value = localStorage.getItem('period') || 28;

  generateCalendar(currentMonth, currentYear);

  document.getElementById('start_date').addEventListener('change', updateCalendarWithPhases);
  document.getElementById('period').addEventListener('change', updateCalendarWithPhases);
  document.getElementById('prev-month').addEventListener('click', () => changeMonth(-1));
  document.getElementById('next-month').addEventListener('click', () => changeMonth(1));
  document.getElementById('clear-cycle').addEventListener('click', clearCycle);

  document.querySelector('.cancel').addEventListener('click', () => {
    const taskInput = document.querySelector('#task-input');
    const txt = taskInput.value.trim();
    if (txt) {
      const startInput = document.getElementById('start_date');
      const periodInput = document.getElementById('period');
      const startDate = startInput.value ? new Date(startInput.value) : null;
      const period = periodInput.value ? parseInt(periodInput.value) : null;
      const phaseInfo = getPhaseInfo(selectedDate, startDate, period);
      saveTask(selectedDate, txt, phaseInfo.phase).then(() => {
        generateCalendar(currentMonth, currentYear);
        updateCalendarWithPhases();
        openModal(selectedDate);
      });
    } else {
      closeModal();
    }
  });

  document.querySelector('.dismiss').addEventListener('click', () => {
    document.querySelector('#task-input').value = '';
    closeModal();
  });

  document.getElementById('taskModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
  });
});

function generateCalendar(month, year) {
  document.getElementById('month-name').textContent = `${monthsRu[month]} ${year}`;
  const daysContainer = document.getElementById('calendar-days');
  daysContainer.innerHTML = '';

  const date = new Date(year, month, 1);
  const firstDay = (date.getDay() + 6) % 7;
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const lastDayPrevMonth = new Date(year, month, 0).getDate();

  for (let i = firstDay - 1; i >= 0; i--) {
    const dayDiv = document.createElement('div');
    dayDiv.classList.add('day', 'prev-month');
    dayDiv.innerText = lastDayPrevMonth - i;
    daysContainer.appendChild(dayDiv);
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const dayDiv = document.createElement('div');
    dayDiv.classList.add('day');
    dayDiv.innerText = day;

    const today = new Date();
    if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
      dayDiv.classList.add('today');
    }

    const tasks = getTasks(new Date(year, month, day));
    if (tasks.length > 0) {
      const taskCount = document.createElement('span');
      taskCount.classList.add('task-count');
      taskCount.innerText = tasks.length;
      dayDiv.appendChild(taskCount);

      const adviceTasks = tasks.filter(t => t && typeof t === 'object' && t.advice && t.advice.trim());
      if (adviceTasks.length > 0) {
        const icon = document.createElement('span');
        icon.classList.add('advice-icon');
        icon.textContent = '💡';
        const combined = adviceTasks.map(t => (t.advice || '').replace(/\s+/g, ' ')).join(' • ');
        icon.title = combined.length > 300 ? combined.slice(0, 300) + '…' : combined;
        dayDiv.appendChild(icon);
      }
    }

    dayDiv.addEventListener('click', () => openModal(new Date(year, month, day)));
    dayDiv.addEventListener('touchstart', (e) => {
      e.preventDefault();
      openModal(new Date(year, month, day));
    }, { passive: false });

    daysContainer.appendChild(dayDiv);
  }

  updateCalendarWithPhases();
}

// ====================== PHASES ==========================
function clearPhases() {
  document.querySelectorAll('.day').forEach(day => {
    day.classList.remove('menstruation', 'follicular', 'ovulation', 'luteal');
  });
}

function calculatePhases(startDate, cycleLength) {
  const dayElements = document.querySelectorAll('#calendar-days .day:not(.prev-month)');
  const baseDate = normalizeDate(new Date(startDate));
  const viewMonth = currentMonth;
  const viewYear = currentYear;

  for (const el of dayElements) {
    const day = parseInt(el.innerText);
    if (isNaN(day)) continue;
    const currentDate = normalizeDate(new Date(viewYear, viewMonth, day));

    const diff = Math.floor((currentDate - baseDate) / (1000 * 3600 * 24));
    if (diff < 0) continue;

    let phase;
    if (diff % cycleLength < 5) phase = 'menstruation';
    else if (diff % cycleLength < cycleLength - 14 - 3) phase = 'follicular';
    else if (diff % cycleLength < cycleLength - 14 + 1) phase = 'ovulation';
    else phase = 'luteal';

    el.classList.add(phase);
  }
}

function updateCalendarWithPhases() {
  const startInput = document.getElementById('start_date');
  const periodInput = document.getElementById('period');
  if (!startInput.value || !periodInput.value) return;

  const [year, month, day] = startInput.value.split('-').map(Number);
  const startDate = new Date(year, month - 1, day);
  const period = parseInt(periodInput.value);
  if (isNaN(startDate.getTime()) || isNaN(period)) return;

  localStorage.setItem('start_date', startInput.value);
  localStorage.setItem('period', periodInput.value);

  clearPhases();
  calculatePhases(startDate, period);
}

function clearCycle() {
  document.getElementById('start_date').value = '';
  document.getElementById('period').value = 28;
  localStorage.removeItem('start_date');
  localStorage.removeItem('period');
  clearPhases();
  generateCalendar(currentMonth, currentYear);
}

function getPhaseInfo(date, startDate, period) {
  if (!startDate || isNaN(startDate.getTime()) || !period || isNaN(period)) {
    return { phase: 'unknown', label: 'Unknown Phase', message: 'Set cycle info', showWarning: false };
  }

  const diff = Math.floor((normalizeDate(date) - normalizeDate(startDate)) / (1000 * 3600 * 24));
  const dayInCycle = diff % period;

  if (dayInCycle < 5) return { phase: 'menstruation', label: 'Menstruation', message: 'Minimize activity. Prioritize rest.', showWarning: true };
  if (dayInCycle < period - 14 - 3) return { phase: 'follicular', label: 'Follicular Phase', message: 'Good time for learning and planning.', showWarning: false };
  if (dayInCycle < period - 14 + 1) return { phase: 'ovulation', label: 'Ovulation', message: 'High energy. Ideal for meetings and social tasks.', showWarning: false };
  return { phase: 'luteal', label: 'Luteal Phase', message: 'Slow down. Delegate tasks and take breaks.', showWarning: true };
}

// ====================== MODAL ==========================
function openModal(date) {
  selectedDate = date;
  const modal = document.getElementById('taskModal');
  modal.style.display = 'flex';

  const phaseBlock = document.querySelector('.phase-block');
  const adviceBlock = document.querySelector('.advice');
  const warningBlock = document.querySelector('.warning');
  const taskInput = document.querySelector('#task-input');
  const taskList = document.querySelector('#task-list');
  const moveDatePicker = document.querySelector('#move-date-picker');
  const dateOptions = document.querySelector('#date-options');
  const confirmMoveBtn = document.querySelector('#confirm-move');

  taskInput.value = '';
  taskList.innerHTML = '';

  const tasksRaw = getTasks(date);
  tasksRaw.forEach((taskRaw, index) => {
    const taskObj = (typeof taskRaw === 'string') ? { text: taskRaw, advice: '' } : taskRaw;

    const taskItem = document.createElement('div');
    taskItem.classList.add('task-item');
    const adviceHtml = taskObj.advice ? `<div class="task-advice"><strong>💡 AI Совет:</strong> ${taskObj.advice}</div>` : '';
    taskItem.innerHTML = `
      <div class="task-body">
        <span class="task-text">${taskObj.text}</span>
        ${adviceHtml}
      </div>
      <div class="task-actions">
        <button class="move-task">Move</button>
        <button class="delete-task">Delete</button>
      </div>
    `;

    taskItem.querySelector('.delete-task').addEventListener('click', () => {
      deleteTask(date, index);
      generateCalendar(currentMonth, currentYear);
      updateCalendarWithPhases();
      openModal(date);
    });

    taskItem.querySelector('.move-task').addEventListener('click', () => {
      selectedTaskIndex = index;
      moveDatePicker.style.display = 'block';
      dateOptions.innerHTML = '';

      const daysToShow = 7;
      const startInput = document.getElementById('start_date');
      const periodInput = document.getElementById('period');
      const startDate = startInput.value ? new Date(startInput.value) : null;
      const period = periodInput.value ? parseInt(periodInput.value) : null;

      for (let i = 1; i <= daysToShow; i++) {
        const nextDate = new Date(date);
        nextDate.setDate(date.getDate() + i);
        const nextPhaseInfo = getPhaseInfo(nextDate, startDate, period);

        const dateOption = document.createElement('div');
        dateOption.classList.add('date-option');
        dateOption.innerHTML = `
          <span>${nextDate.getDate()}-${nextDate.getMonth() + 1}</span>
          <small>${nextPhaseInfo.label}</small>
          <div class="phase-dot ${nextPhaseInfo.showWarning ? 'warning' : 'good'}"></div>
        `;
        dateOption.addEventListener('click', () => {
          document.querySelectorAll('.date-option').forEach(opt => opt.classList.remove('selected'));
          dateOption.classList.add('selected');
          moveToDate = nextDate;
          confirmMoveBtn.style.display = 'block';
        });
        dateOptions.appendChild(dateOption);
      }
    });

    taskList.appendChild(taskItem);
  });

  const startInput = document.getElementById('start_date');
  const periodInput = document.getElementById('period');
  const startDate = startInput.value ? new Date(startInput.value) : null;
  const period = periodInput.value ? parseInt(periodInput.value) : null;
  const phaseInfo = getPhaseInfo(date, startDate, period);

  phaseBlock.innerHTML = `
    <div class="dot ${phaseInfo.phase}"></div>
    <div><strong>${phaseInfo.label}</strong><br><small>${phaseInfo.message}</small></div>
  `;
  adviceBlock.innerHTML = `<strong>Advice</strong><br>${phaseInfo.message}`;
  warningBlock.style.display = phaseInfo.showWarning ? 'block' : 'none';

  confirmMoveBtn.onclick = () => {
    if (selectedTaskIndex !== null && moveToDate) {
      moveTask(selectedDate, moveToDate, selectedTaskIndex);
      generateCalendar(currentMonth, currentYear);
      updateCalendarWithPhases();
      openModal(date);
    }
  };
}

function closeModal() {
  document.getElementById('taskModal').style.display = 'none';
  document.getElementById('move-date-picker').style.display = 'none';
  document.getElementById('confirm-move').style.display = 'none';
  selectedTaskIndex = null;
  moveToDate = null;
}
