document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video")
    const canvas = document.getElementById("canvas")
    const startButton = document.getElementById("startButton")
    const switchCameraButton = document.getElementById("switchCameraButton")
    const statusText = document.getElementById("statusText")
    const statusBar = document.querySelector(".status-bar")
    const resultText = document.getElementById("resultText")
    const openLinkBtn = document.getElementById("openLinkBtn")
  
    let scanning = false
    let currentStream = null
    const canvasContext = canvas.getContext("2d")
    let currentFacingMode = "environment" // Start with back camera
  
    // Modal instance
    const resultModal = new bootstrap.Modal(document.getElementById("resultModal"))
  
    // Check if the browser supports getUserMedia
    function hasGetUserMedia() {
      return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia)
    }
  
    // Start the QR scanner
    startButton.addEventListener("click", () => {
      if (scanning) {
        stopScanner()
      } else {
        startScanner()
      }
    })
  
    // Switch between front and back cameras
    switchCameraButton.addEventListener("click", () => {
      if (currentStream) {
        stopMediaTracks(currentStream)
        currentFacingMode = currentFacingMode === "environment" ? "user" : "environment"
        startScanner()
      }
    })
  
    function startScanner() {
      if (!hasGetUserMedia()) {
        updateStatus("error", "Your browser does not support camera access")
        return
      }
  
      updateStatus("scanning", "Accessing camera...")
  
      const constraints = {
        video: {
          facingMode: currentFacingMode,
          width: { ideal: 1280 },
          height: { ideal: 720 },
        },
      }
  
      navigator.mediaDevices
        .getUserMedia(constraints)
        .then((stream) => {
          currentStream = stream
          video.srcObject = stream
          video.setAttribute("playsinline", true) // Required for iOS
  
          return video.play()
        })
        .then(() => {
          scanning = true
          startButton.textContent = "Stop Scanner"
          startButton.classList.remove("btn-primary")
          startButton.classList.add("btn-danger")
  
          // Show switch camera button if multiple cameras are available
          navigator.mediaDevices.enumerateDevices().then((devices) => {
            const videoDevices = devices.filter((device) => device.kind === "videoinput")
            if (videoDevices.length > 1) {
              switchCameraButton.classList.remove("d-none")
            }
          })
  
          updateStatus("scanning", "Scanning for QR code...")
  
          // Start scanning for QR codes
          requestAnimationFrame(tick)
        })
        .catch((error) => {
          console.error("Error accessing the camera:", error)
          updateStatus("error", "Could not access the camera")
        })
    }
  
    function stopScanner() {
      if (currentStream) {
        stopMediaTracks(currentStream)
        currentStream = null
      }
  
      scanning = false
      startButton.textContent = "Start Scanner"
      startButton.classList.remove("btn-danger")
      startButton.classList.add("btn-primary")
      switchCameraButton.classList.add("d-none")
  
      updateStatus("", "Ready to scan")
    }
  
    function stopMediaTracks(stream) {
      stream.getTracks().forEach((track) => {
        track.stop()
      })
      video.srcObject = null
    }
  
    function tick() {
      if (!scanning) return
  
      if (video.readyState === video.HAVE_ENOUGH_DATA) {
        // Draw the video frame to the canvas
        canvas.height = video.videoHeight
        canvas.width = video.videoWidth
        canvasContext.drawImage(video, 0, 0, canvas.width, canvas.height)
  
        // Get the image data from the canvas
        const imageData = canvasContext.getImageData(0, 0, canvas.width, canvas.height)
  
        // Scan for QR code
        const code = jsQR(imageData.data, imageData.width, imageData.height, {
          inversionAttempts: "dontInvert",
        })
  
        if (code) {
          // QR code found
          console.log("QR Code detected:", code.data)
  
          // Play success sound or vibration
          if (navigator.vibrate) {
            navigator.vibrate(200)
          }
  
          // Update status
          updateStatus("success", "QR code found!")
  
          // Show the result in the modal
          showResult(code.data)
  
          // Pause scanning
          scanning = false
          startButton.textContent = "Start Scanner"
          startButton.classList.remove("btn-danger")
          startButton.classList.add("btn-primary")
        }
      }
  
      // Continue scanning
      if (scanning) {
        requestAnimationFrame(tick)
      }
    }
  
    function showResult(data) {
      resultText.textContent = data
  
      // Check if the result is a URL
      let url = data
      if (!data.startsWith("http://") && !data.startsWith("https://")) {
        url = "https://" + data
      }
  
      openLinkBtn.href = url
  
      // Show the modal
      resultModal.show()
  
      // When modal is closed, resume scanning
      document.getElementById("resultModal").addEventListener("hidden.bs.modal", () => {
        if (!scanning) {
          updateStatus("", "Ready to scan")
        }
      })
    }
  
    function updateStatus(state, message) {
      statusText.textContent = message
  
      // Remove all state classes
      statusBar.classList.remove("scanning", "success", "error")
  
      // Add the current state class
      if (state) {
        statusBar.classList.add(state)
      }
    }
  })
  
  