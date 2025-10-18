const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const signupBtn = document.getElementById('signup-btn');
const signinBtn = document.getElementById('signin-btn');
const errorMessage = document.getElementById('error-message');

function showError(message) {
    errorMessage.textContent = message;
    setTimeout(() => {
        errorMessage.textContent = '';
    }, 5000);
}

function validatePasswordFormat(password) {
    if (password.length === 3) {
        return /^[234]{3}$/.test(password);
    }
    if (password.length === 5) {
        return /^\d{5}$/.test(password);
    }
    if (password.length === 6) {
        return /^[a-zA-Z0-9+*]{6}$/.test(password);
    }
    return false;
}

async function handleSignup() {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    if (!validatePasswordFormat(password)) {
        showError('Invalid password format. Please follow the password requirements.');
        return;
    }

    try {
        const response = await fetch('/api/auth/signup', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = '/home';
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Connection error. Please try again.');
        console.error('Error:', error);
    }
}

async function handleSignin() {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !password) {
        showError('Please enter both email and password');
        return;
    }

    try {
        const response = await fetch('/api/auth/signin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (data.success) {
            window.location.href = '/home';
        } else {
            showError(data.message);
        }
    } catch (error) {
        showError('Connection error. Please try again.');
        console.error('Error:', error);
    }
}

signupBtn.addEventListener('click', handleSignup);
signinBtn.addEventListener('click', handleSignin);

passwordInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        handleSignin();
    }
});
