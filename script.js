const form = document.getElementById('itemForm');
const container = document.getElementById('itemContainer');

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const name = document.getElementById('itemName').value;
  const description = document.getElementById('itemDescription').value;
  const grade = document.getElementById('itemGrade').value;
  const imageFile = document.getElementById('itemImage').files[0];

  if (!imageFile) return;

  const reader = new FileReader();

  reader.onload = function() {
    const itemCard = document.createElement('div');
    itemCard.classList.add('item-card');
    itemCard.innerHTML = `
      <img src="${reader.result}" alt="${name}">
      <div class="item-content">
        <h3>${name}</h3>
        <p>${description}</p>
        <span class="grade ${grade}">Grade ${grade}</span>
      </div>
    `;
    container.appendChild(itemCard);
  };

  reader.readAsDataURL(imageFile);
  form.reset();
});
