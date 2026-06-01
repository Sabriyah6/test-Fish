

// Logika fungsional menu dropdown mobile (Buka-Tutup & Animasi Silang)
const menuToggle = document.getElementById('menuToggle');
const mobileMenu = document.getElementById('mobileMenu');

if (menuToggle && mobileMenu) {
    menuToggle.addEventListener('click', function () {
        this.classList.toggle('active');
        mobileMenu.classList.toggle('open');
    });

    // Menutup otomatis jika salah satu navigasi di dalam mobile menu ditekan
    mobileMenu.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            menuToggle.classList.remove('active');
            mobileMenu.classList.remove('open');
        });
    });
}

// JavaScript Hamburger Menu (Sama dengan Beranda)
const ham = document.getElementById('ham');
const menu = document.getElementById('mobileMenu');

ham.addEventListener('click', () => {
    ham.classList.toggle('open');
    menu.classList.toggle('open');
});

// Otomatis tutup menu jika link diklik
menu.querySelectorAll('a').forEach(a => {
    a.addEventListener('click', () => {
        ham.classList.remove('open');
        menu.classList.remove('open');
    });
});
