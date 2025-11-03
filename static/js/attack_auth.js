// attack_auth.js - Corrected version (No fake simulation)

const targetUsernameInput = document.getElementById("target-username")
const attackOptions = document.querySelectorAll(".attack-option")
const startAttackBtn = document.getElementById("start-attack")
const backBtn = document.getElementById("back-btn")
const errorMessage = document.getElementById("error-message")
const successMessage = document.getElementById("success-message")
const attackProgress = document.getElementById("attack-progress")
const progressFill = document.getElementById("progress-fill")
const progressText = document.getElementById("progress-text")
const attackLog = document.getElementById("attack-log")

let selectedMethod = null
let isAttackRunning = false

// Select attack method
attackOptions.forEach(option => {
    option.addEventListener("click", () => {
        if (isAttackRunning) return
        
        attackOptions.forEach(opt => opt.classList.remove("selected"))
        option.classList.add("selected")
        selectedMethod = option.dataset.method
    })
})

// Add log entry
function addLogEntry(message, type = "trying") {
    const logEntry = document.createElement("div")
    logEntry.className = `log-entry log-${type}`
    logEntry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`
    attackLog.appendChild(logEntry)
    attackLog.scrollTop = attackLog.scrollHeight
}

// Update progress
function updateProgress(percentage, message) {
    progressFill.style.width = `${percentage}%`
    progressText.textContent = `${Math.round(percentage)}% - ${message}`
}

// Start attack
async function startAttack() {
    if (isAttackRunning) return
    
    const username = targetUsernameInput.value.trim()
    
    if (!username) {
        showError("Veuillez entrer un nom d'utilisateur")
        return
    }
    
    if (!selectedMethod) {
        showError("Veuillez sélectionner une méthode d'attaque")
        return
    }
    
    // Reset UI
    errorMessage.textContent = ""
    successMessage.textContent = ""
    attackProgress.style.display = "block"
    attackLog.style.display = "block"
    attackLog.innerHTML = ""
    updateProgress(0, "Vérification de l'utilisateur...")
    isAttackRunning = true
    startAttackBtn.disabled = true
    
    try {
        // Check if user exists
        addLogEntry(`🔍 Vérification de l'existence de l'utilisateur: ${username}`, "trying")
        const checkResponse = await fetch("/api/attack_auth/check-user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username }),
        })
        
        const checkData = await checkResponse.json()
        
        if (!checkData.exists) {
            showError("❌ Utilisateur non trouvé")
            addLogEntry("❌ Utilisateur non trouvé dans la base de données", "error")
            isAttackRunning = false
            startAttackBtn.disabled = false
            return
        }
        
        addLogEntry("✅ Utilisateur trouvé, lancement de l'attaque...", "success")
        updateProgress(10, "Préparation de l'attaque...")
        
        // Add method-specific info
        if (selectedMethod === 'dictionary3') {
            addLogEntry("📚 Mode: Attaque par dictionnaire (3 caractères)", "trying");
        } else if (selectedMethod === 'dictionary5') {
            addLogEntry("📚 Mode: Attaque par dictionnaire (5 chiffres)", "trying");
        } else if (selectedMethod === 'bruteforce') {
            addLogEntry("💥 Mode: Force brute (6 caractères: a-z, A-Z, 0-9, +, *)", "trying");
        }
        
        // Start the actual attack
        const attackResponse = await fetch("/api/attack_auth/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ 
                username, 
                method: selectedMethod 
            }),
        })
        
        const attackData = await attackResponse.json()
        
        if (attackData.success) {
            // *** THIS IS THE FIX ***
            // Instead of simulating, just show the real result immediately.
            showAttackResult(username, attackData)
        } else {
            showError(attackData.message)
            isAttackRunning = false
            startAttackBtn.disabled = false
        }
        
    } catch (error) {
        showError("Erreur de connexion au serveur")
        console.error("Attack error:", error)
        isAttackRunning = false
        startAttackBtn.disabled = false
    }
}

// NEW FUNCTION: Displays the final result from the server
function showAttackResult(username, attackData) {
    let foundPassword = null;

    if (attackData.found) {
        foundPassword = attackData.password;
        addLogEntry(`🎉 MOT DE PASSE TROUVÉ: ${foundPassword}`, "success");
        addLogEntry(`📊 Tentatives: ${attackData.attempts.toLocaleString()}`, "success");
        addLogEntry(`⏱️ Durée: ${attackData.duration.toFixed(2)}s`, "success");
        updateProgress(100, "Attaque terminée avec succès!");
        successMessage.textContent = `Mot de passe trouvé: ${foundPassword}`;
        
        // Auto-login after 3 seconds
        setTimeout(() => {
            attemptAutoLogin(username, foundPassword);
        }, 3000);
    } else {
        addLogEntry("❌ Aucun mot de passe trouvé avec cette méthode", "error");
        addLogEntry(`📊 Tentatives: ${attackData.attempts.toLocaleString()}`, "trying");
        addLogEntry(`⏱️ Durée: ${attackData.duration.toFixed(2)}s`, "trying");
        updateProgress(100, "Attaque terminée - Aucun résultat");
        successMessage.textContent = "Aucun mot de passe trouvé. Essayez une autre méthode.";
    }
    
    isAttackRunning = false;
    startAttackBtn.disabled = false;
}

// DELETED: simulateAttackProgress() (No longer needed)
// DELETED: generateRealisticPassword() (No longer needed)

async function attemptAutoLogin(username, password) {
    addLogEntry("🔐 Tentative de connexion automatique...", "success")
    
    try {
        const response = await fetch("/api/auth/signin", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username, password }),
        })
        
        const data = await response.json()
        
        if (data.success) {
            addLogEntry("✅ Connexion réussie! Redirection...", "success")
            setTimeout(() => {
                window.location.href = "/home"
            }, 1000)
        } else {
            addLogEntry("❌ Échec de la connexion automatique", "error")
        }
    } catch (error) {
        addLogEntry("❌ Erreur lors de la connexion automatique", "error")
    }
}

function showError(message) {
    errorMessage.textContent = message
    setTimeout(() => {
        errorMessage.textContent = ""
    }, 5000)
}

function goBack() {
    window.location.href = "/auth"
}

// Event listeners
startAttackBtn.addEventListener("click", startAttack)
backBtn.addEventListener("click", goBack)

targetUsernameInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        startAttack()
    }
})

// Initialize
attackLog.innerHTML = '<div class="log-entry">Prêt à lancer une attaque...</div>'