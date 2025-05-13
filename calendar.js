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
let selectedTaskIndex = null; // Для хранения индекса задачи, которую переносим
let selectedDate = null; // Текущая дата задачи
let moveToDate = null; // Новая дата для переноса

function normalizeDate(d) {
  return new Date(d.getFullYear(), d.getMonth(), d.getDate());
}

// Функции для работы с задачами
function saveTask(date, task) {
  const key = `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  try {
    let tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
    if (!tasks[key]) tasks[key] = [];
    tasks[key].push(task);
    localStorage.setItem('tasks', JSON.stringify(tasks));
  } catch (e) {
    console.error('Failed to save task:', e);
    alert('Error saving task. Try disabling private browsing.');
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
  try {
    let tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
    if (tasks[key] && tasks[key].length > taskIndex) {
      tasks[key].splice(taskIndex, 1);
      if (tasks[key].length === 0) {
        delete tasks[key];
      }
      localStorage.setItem('tasks', JSON.stringify(tasks));
    }
  } catch (e) {
    console.error('Failed to delete task:', e);
    alert('Error deleting task.');
  }
}

function moveTask(fromDate, toDate, taskIndex) {
  const fromKey = `${fromDate.getFullYear()}-${fromDate.getMonth()}-${fromDate.getDate()}`;
  const toKey = `${toDate.getFullYear()}-${toDate.getMonth()}-${toDate.getDate()}`;
  try {
    let tasks = JSON.parse(localStorage.getItem('tasks') || '{}');
    if (tasks[fromKey] && tasks[fromKey].length > taskIndex) {
      const task = tasks[fromKey][taskIndex];
      tasks[fromKey].splice(taskIndex, 1);
      if (tasks[fromKey].length === 0) {
        delete tasks[fromKey];
      }
      if (!tasks[toKey]) tasks[toKey] = [];
      tasks[toKey].push(task);
      localStorage.setItem('tasks', JSON.stringify(tasks));
    }
  } catch (e) {
    console.error('Failed to move task:', e);
    alert('Error moving task.');
  }
}

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
  document.querySelector('.cancel').addEventListener('click', closeModal);
  document.querySelector('.dismiss').addEventListener('click', () => {
    const taskInput = document.querySelector('#task-input');
    if (taskInput) {
      taskInput.value = '';
    }
    closeModal();
  });

  // Закрытие модального окна по клику на фон
  document.getElementById('taskModal').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) closeModal();
  });

  // Закрытие модального окна по Esc
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
    if (
      day === today.getDate() &&
      month === today.getMonth() &&
      year === today.getFullYear()
    ) {
      dayDiv.classList.add('today');
    }

    const tasks = getTasks(new Date(year, month, day));
    if (tasks.length > 0) {
      const taskCount = document.createElement('span');
      taskCount.classList.add('task-count');
      taskCount.innerText = tasks.length;
      dayDiv.appendChild(taskCount);
    }

    dayDiv.addEventListener('click', () => {
      const selectedDate = new Date(year, month, day);
      openModal(selectedDate);
    });
    dayDiv.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const selectedDate = new Date(year, month, day);
      openModal(selectedDate);
    }, { passive: false });

    daysContainer.appendChild(dayDiv);
  }

  updateCalendarWithPhases();
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

function clearPhases() {
  document.querySelectorAll('.day').forEach(day => {
    day.classList.remove('menstruation', 'follicular', 'ovulation', 'luteal');
  });
}

function addPhase(dayElement, phase) {
  dayElement.classList.add(phase);
}

function calculatePhases(startDate, cycleLength) {
  const daysContainer = document.getElementById('calendar-days');
  const dayElements = daysContainer.querySelectorAll('.day:not(.prev-month)');
  const baseDate = normalizeDate(new Date(startDate));
  const viewMonth = currentMonth;
  const viewYear = currentYear;

  const dayMap = Array.from(dayElements)
    .map(el => ({
      el,
      day: parseInt(el.innerText)
    }))
    .filter(d => !isNaN(d.day));

  const numberOfCyclesToPredict = 3;

  for (const { el, day } of dayMap) {
    const currentDate = normalizeDate(new Date(viewYear, viewMonth, day));

    for (let cycleOffset = 0; cycleOffset < numberOfCyclesToPredict; cycleOffset++) {
      const cycleStartDate = new Date(baseDate);
      cycleStartDate.setDate(baseDate.getDate() + cycleOffset * cycleLength);
      const diff = Math.floor((currentDate - normalizeDate(cycleStartDate)) / (1000 * 3600 * 24));

      if (diff < 0 || diff >= cycleLength) continue;

      let phase;
      if (diff < 5) phase = 'menstruation';
      else if (diff < cycleLength - 14 - 3) phase = 'follicular';
      else if (diff < cycleLength - 14 + 1) phase = 'ovulation';
      else phase = 'luteal';

      addPhase(el, phase);
      break;
    }
  }
}

function updateCalendarWithPhases() {
  const startInput = document.getElementById('start_date');
  const periodInput = document.getElementById('period');

  if (!startInput.value || !periodInput.value) return;

  const [year, month, day] = startInput.value.split('-').map(Number);
  const startDate = new Date(year, month - 1, day);
  const period = parseInt(periodInput.value);

  try {
    localStorage.setItem('start_date', startInput.value);
    localStorage.setItem('period', periodInput.value);
  } catch (e) {
    console.error('Failed to save cycle data:', e);
    alert('Error saving cycle data.');
  }

  if (isNaN(startDate.getTime()) || isNaN(period)) return;

  clearPhases();
  calculatePhases(startDate, period);
}

function clearCycle() {
  document.getElementById('start_date').value = '';
  document.getElementById('period').value = 28;
  try {
    localStorage.removeItem('start_date');
    localStorage.removeItem('period');
  } catch (e) {
    console.error('Failed to clear cycle data:', e);
  }
  clearPhases();
  generateCalendar(currentMonth, currentYear);
}

function getPhaseInfo(date, startDate, period) {
  if (!startDate || isNaN(startDate.getTime()) || !period || isNaN(period)) {
    return { phase: 'unknown', label: 'Unknown Phase', message: 'Set cycle info', showWarning: false };
  }

  const diff = Math.floor(
    (normalizeDate(date) - normalizeDate(startDate)) / (1000 * 3600 * 24)
  );

  let phase = '';
  let label = '';
  let message = '';
  let showWarning = false;

  if (diff < 0 || diff >= period) {
    phase = 'unknown';
    label = 'Unknown Phase';
    message = 'Outside cycle period';
    showWarning = false;
  } else if (diff < 5) {
    phase = 'menstruation';
    label = 'Menstruation';
    message = 'Minimize activity. Prioritize rest.';
    showWarning = true;
  } else if (diff < period - 14 - 3) {
    phase = 'follicular';
    label = 'Follicular Phase';
    message = 'Good time for learning and planning.';
    showWarning = false;
  } else if (diff < period - 14 + 1) {
    phase = 'ovulation';
    label = 'Ovulation';
    message = 'High energy. Ideal for meetings and social tasks.';
    showWarning = false;
  } else {
    phase = 'luteal';
    label = 'Luteal Phase';
    message = 'Slow down. Delegate tasks and take breaks.';
    showWarning = true;
  }

  return { phase, label, message, showWarning };
}

function openModal(date) {
  const modal = document.getElementById('taskModal');
  modal.style.display = 'flex';

  selectedDate = date; // Сохраняем текущую дату

  const monthsRuShort = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ];

  const phaseBlock = document.querySelector('.phase-block');
  const adviceBlock = document.querySelector('.advice');
  const warningBlock = document.querySelector('.warning');
  const taskInput = document.querySelector('#task-input');
  const taskList = document.querySelector('#task-list');
  const moveDatePicker = document.querySelector('#move-date-picker');
  const dateOptions = document.querySelector('#date-options');
  const confirmMoveBtn = document.querySelector('#confirm-move');

  taskInput.value = '';

  // Отображаем список задач
  const tasks = getTasks(date);
  taskList.innerHTML = '';
  tasks.forEach((task, index) => {
    const taskItem = document.createElement('div');
    taskItem.classList.add('task-item');
    taskItem.innerHTML = `
      <span>${task}</span>
      <div>
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
      selectedTaskIndex = index; // Сохраняем индекс задачи
      moveDatePicker.style.display = 'block';
      dateOptions.innerHTML = '';

      // Показываем ближайшие 7 дней для переноса
      const daysToShow = 7;
      const startInput = document.getElementById('start_date');
      const periodInput = document.getElementById('period');
      const startDate = startInput.value ? new Date(startInput.value) : null;
      const period = periodInput.value ? parseInt(periodInput.value) : null;

      for (let i = 1; i <= daysToShow; i++) {
        const nextDate = new Date(date);
        nextDate.setDate(date.getDate() + i);
        const nextDay = nextDate.getDate();
        const nextMonth = monthsRuShort[nextDate.getMonth()];
        const nextYear = nextDate.getFullYear();

        const nextPhaseInfo = getPhaseInfo(nextDate, startDate, period);
        const dateOption = document.createElement('div');
        dateOption.classList.add('date-option');
        dateOption.innerHTML = `
          <span>${nextDay} ${nextMonth}</span>
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

  // Логика подтверждения переноса
  confirmMoveBtn.onclick = () => {
    if (selectedTaskIndex !== null && moveToDate) {
      moveTask(selectedDate, moveToDate, selectedTaskIndex);
      generateCalendar(currentMonth, currentYear);
      updateCalendarWithPhases();
      openModal(date);
    }
  };

  // Сохранение задачи
  const keepBtn = document.querySelector('.cancel');
  keepBtn.onclick = () => {
    if (taskInput.value.trim()) {
      saveTask(date, taskInput.value.trim());
      generateCalendar(currentMonth, currentYear);
      updateCalendarWithPhases();
      openModal(date);
    } else {
      closeModal();
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