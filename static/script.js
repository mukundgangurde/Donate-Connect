document.querySelectorAll('nav ul li a').forEach(anchor => {
    anchor.addEventListener('click', function (event) {
        const target = this.getAttribute('href');

        // Check if the href is an internal section link (starts with #)
        if (target.startsWith("#")) {
            event.preventDefault();
            document.querySelector(target).scrollIntoView({ behavior: 'smooth' });
        }
    });
});

window.addEventListener("scroll", function () {
    let btn = document.getElementById("backToTop");
    btn.style.display = window.scrollY > 300 ? "block" : "none";
});


fetch("http://127.0.0.1:5000/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: email, password: password })
})
    .then(response => response.json())
    .then(data => alert(data.message))
    .catch(error => console.error("Error:", error));

document.getElementById("backToTop").addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
});

// Profile section
document.addEventListener('DOMContentLoaded', () => {
    const profileToggle = document.getElementById('profileToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');

    profileToggle.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevent click event from bubbling up
        dropdownMenu.style.display = dropdownMenu.style.display === 'block' ? 'none' : 'block';
    });

    document.addEventListener('click', (event) => {
        if (!profileToggle.contains(event.target)) {
            dropdownMenu.style.display = 'none';
        }
    });
});

// Profile form
  // Get DOM Elements
  const modal = document.getElementById("profileModal");
  const openBtn = document.getElementById("openProfileModal");
  const closeBtn = document.querySelector(".close-btn");
  
  // Open Modal
  openBtn.onclick = function() {
    modal.style.display = "block";
  }

  // Close Modal
  closeBtn.onclick = function() {
    modal.style.display = "none";
  }

  // Close modal if user clicks outside modal content
  window.onclick = function(event) {
    if (event.target == modal) {
      modal.style.display = "none";
    }
  }

  // Initialize Leaflet Map
  let map = L.map('map').setView([20.5937, 78.9629], 5); // Centered on India, zoom level 5
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
  }).addTo(map);

  // Create marker
  let marker = L.marker([20.5937, 78.9629], {draggable: true}).addTo(map);

  // Update hidden fields on marker drag
  marker.on('dragend', function(e) {
    let lat = marker.getLatLng().lat;
    let lng = marker.getLatLng().lng;
    document.getElementById('latitude').value = lat;
    document.getElementById('longitude').value = lng;
  });
