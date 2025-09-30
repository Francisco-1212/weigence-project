const notificationButton = document.getElementById('notification-button');
const notificationPanel = document.getElementById('notification-panel');
const closeNotificationPanel = document.getElementById('close-notification-panel');
const notificationBackdrop = document.getElementById('notification-backdrop');
const mainContent = document.querySelector('.flex-col.h-screen');

function openPanel() {
  notificationPanel.classList.remove('translate-x-full');
  notificationBackdrop.classList.remove('opacity-0', 'pointer-events-none');
  mainContent.classList.add('[filter:blur(8px)]');
  notificationPanel.focus();
}

function closePanel() {
  notificationPanel.classList.add('translate-x-full');
  notificationBackdrop.classList.add('opacity-0', 'pointer-events-none');
  mainContent.classList.remove('[filter:blur(8px)]');
  notificationButton.focus();
}

notificationButton.addEventListener('click', e => {
  e.stopPropagation();
  openPanel();
});

closeNotificationPanel.addEventListener('click', closePanel);
notificationBackdrop.addEventListener('click', closePanel);

document.addEventListener('keydown', e => {
  if(e.key === "Escape" && !notificationPanel.classList.contains('translate-x-full')) {
     closePanel();
  }
});
