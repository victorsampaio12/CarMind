document.addEventListener("DOMContentLoaded", function () {
    const toggleIcons = document.querySelectorAll(".toggle-password");

    toggleIcons.forEach(icon => {
        icon.addEventListener("click", () => {
            const targetId = icon.getAttribute("data-target");
            const input = document.getElementById(targetId);

            if (input) {
                const isPassword = input.type === "password";
                input.type = isPassword ? "text" : "password";
                icon.src = isPassword
                    ? "/static/imagens/eye-slash.png"
                    : "/static/imagens/eye.png";
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const phoneInput = document.getElementById('phone');
    if (phoneInput) {
        IMask(phoneInput, {
            mask: '(00) 00000-0000'
        });
    }
});
