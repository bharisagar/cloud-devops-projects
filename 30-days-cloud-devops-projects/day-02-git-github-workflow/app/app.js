const checks = [
  'I created a feature branch.',
  'I reviewed git diff before commit.',
  'I used a meaningful commit message.',
  'I wrote a pull-request style summary.',
  'I captured evidence screenshots.',
];

const list = document.querySelector('#checks');

checks.forEach((check) => {
  const item = document.createElement('li');
  item.textContent = check;
  list.appendChild(item);
});
