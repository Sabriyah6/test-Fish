
// Ambil elemen berdasarkan ID asli yang ada di tentang.html kamu
const menuToggle = document.getElementById('menuToggle');
const navMenu = document.querySelector('.nav-menu');

if (menuToggle && navMenu) {
    menuToggle.addEventListener('click', function (e) {
        e.stopPropagation();
        menuToggle.classList.toggle('open');
        navMenu.classList.toggle('open'); // Ini akan memunculkan menu di HP & Tab
    });

    // Menutup menu otomatis jika klik di luar area menu
    document.addEventListener('click', function (e) {
        if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
            menuToggle.classList.remove('open');
            navMenu.classList.remove('open');
        }
    });
}
