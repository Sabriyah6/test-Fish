
const ham = document.getElementById('ham');
const menu = document.getElementById('mobileMenu');

if (ham && menu) {
    ham.addEventListener('click', function (e) {
        e.stopPropagation();
        ham.classList.toggle('open');
        menu.classList.toggle('open');
    });

    // Menutup menu mobile secara otomatis jika mengklik area di luar menu
    document.addEventListener('click', function (e) {
        if (!menu.contains(e.target) && !ham.contains(e.target)) {
            ham.classList.remove('open');
            menu.classList.remove('open');
        }
    });
}