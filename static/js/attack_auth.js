// attack_auth.js - JavaScript for the attack authentication page

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
            // Simulate attack progress with real algorithm simulation
            simulateAttackProgress(username, selectedMethod, attackData)
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

// Simulate attack progress with realistic patterns
function simulateAttackProgress(username, method, attackData) {
    let progress = 10
    const totalSteps = method === "dictionary" ? 150 : 300
    let foundPassword = null
    
    const interval = setInterval(() => {
        if (progress >= 100) {
            clearInterval(interval)
            if (!foundPassword) {
                addLogEntry("❌ Aucun mot de passe trouvé avec cette méthode", "error")
                updateProgress(100, "Attaque terminée - Aucun résultat")
                successMessage.textContent = "Aucun mot de passe trouvé. Essayez une autre méthode."
            }
            isAttackRunning = false
            startAttackBtn.disabled = false
            return
        }
        
        progress += Math.random() * 8
        progress = Math.min(progress, 100)
        
        // Generate realistic password attempts based on method
        const currentPassword = generateRealisticPassword(method, progress)
        
        addLogEntry(`🔑 Test du mot de passe: ${currentPassword}`, "trying")
        
        const phase = progress < 33 ? "Phase 1" : progress < 66 ? "Phase 2" : "Phase 3"
        const testedPercentage = Math.round(progress/totalSteps*100)
        updateProgress(progress, `${phase} - Testé ${testedPercentage}% des combinaisons`)
        
        // Simulate finding password (more likely in later stages)
        if (progress >= 70 && Math.random() < 0.15) {
            clearInterval(interval)
            foundPassword = attackData.password || generateRealisticPassword(method, 100)
            addLogEntry(`🎉 MOT DE PASSE TROUVÉ: ${foundPassword}`, "success")
            updateProgress(100, "Attaque terminée avec succès!")
            successMessage.textContent = `Mot de passe trouvé: ${foundPassword}`
            
            // Auto-login after 3 seconds
            setTimeout(() => {
                attemptAutoLogin(username, foundPassword)
            }, 3000)
            isAttackRunning = false
            startAttackBtn.disabled = false
        }
    }, 300) // Update every 300ms for realistic feel
}

function generateRealisticPassword(method, progress) {
    if (method === "dictionary") {
        const dictionary = [
            "234", "432", "12345", "54321", "11111", "123456", 
            "password", "qwerty", "admin", "secret", "test", 
            "123", "321", "00000", "q7*88+", "hello", "welcome"
        ]
        const index = Math.floor((progress / 100) * dictionary.length)
        return dictionary[Math.min(index, dictionary.length - 1)]
    } else {
        // Brute force - generate based on progress and realistic patterns
        if (progress < 33) {
            // Phase 1: 3-character passwords
            const chars = "234"
            let password = ""
            for (let i = 0; i < 3; i++) {
                password += chars[Math.floor(Math.random() * chars.length)]
            }
            return password
        } else if (progress < 66) {
            // Phase 2: 5-digit passwords
            let password = ""
            for (let i = 0; i < 5; i++) {
                password += Math.floor(Math.random() * 10)
            }
            return password
        } else {
            // Phase 3: 6-character passwords
            const chars = "abcdefghijklmnopqrstuvwxyz0123456789+*"
            let password = ""
            for (let i = 0; i < 6; i++) {
                password += chars[Math.floor(Math.random() * chars.length)]
            }
            return password
        }
    }
}

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

// Enter key support
targetUsernameInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        startAttack()
    }
})

// Initialize
attackLog.innerHTML = '<div class="log-entry">Prêt à lancer une attaque...</div>'