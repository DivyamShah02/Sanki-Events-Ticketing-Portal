// Wait for the DOM to be fully loaded
document.addEventListener("DOMContentLoaded", () => {
    // Hide loader when page is loaded
    window.addEventListener("load", () => {
      const loader = document.getElementById("loader")
      loader.style.opacity = "0"
      setTimeout(() => {
        loader.style.display = "none"
      }, 500)
    })
  
    // Initialize Three.js background
    initThreeJsBackground()
  
    // Initialize header scroll effect
    initHeaderScroll()
  
    // Initialize back to top button
    initBackToTop()
  
    // Initialize search and filter functionality
    initSearchAndFilter()
  
    // Initialize parallax effects
    initParallaxEffects()
  
    // Initialize form validation
    initFormValidation()
  })
  
  // Three.js Background
  function initThreeJsBackground() {
    const canvas = document.getElementById("bg-canvas")
  
    // Create scene, camera, and renderer
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000)
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
  
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(window.devicePixelRatio)
  
    // Create particles
    const particlesGeometry = new THREE.BufferGeometry()
    const particlesCount = 2000
  
    const posArray = new Float32Array(particlesCount * 3)
    const colorsArray = new Float32Array(particlesCount * 3)
  
    // Fill positions and colors arrays
    for (let i = 0; i < particlesCount * 3; i += 3) {
      // Positions
      posArray[i] = (Math.random() - 0.5) * 10
      posArray[i + 1] = (Math.random() - 0.5) * 10
      posArray[i + 2] = (Math.random() - 0.5) * 10
  
      // Colors - neon pink/purple theme
      colorsArray[i] = Math.random() * 0.5 + 0.5 // R
      colorsArray[i + 1] = Math.random() * 0.2 // G
      colorsArray[i + 2] = Math.random() * 0.5 + 0.5 // B
    }
  
    particlesGeometry.setAttribute("position", new THREE.BufferAttribute(posArray, 3))
    particlesGeometry.setAttribute("color", new THREE.BufferAttribute(colorsArray, 3))
  
    // Material
    const particlesMaterial = new THREE.PointsMaterial({
      size: 0.02,
      transparent: true,
      opacity: 0.8,
      vertexColors: true,
      blending: THREE.AdditiveBlending,
    })
  
    // Create points
    const particlesMesh = new THREE.Points(particlesGeometry, particlesMaterial)
    scene.add(particlesMesh)
  
    // Position camera
    camera.position.z = 5
  
    // Mouse movement effect
    let mouseX = 0
    let mouseY = 0
  
    document.addEventListener("mousemove", (event) => {
      mouseX = (event.clientX / window.innerWidth) * 2 - 1
      mouseY = -(event.clientY / window.innerHeight) * 2 + 1
    })
  
    // Handle window resize
    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    })
  
    // Animation loop
    function animate() {
      requestAnimationFrame(animate)
  
      // Rotate particles
      particlesMesh.rotation.x += 0.0005
      particlesMesh.rotation.y += 0.0005
  
      // Mouse interaction
      particlesMesh.rotation.x += mouseY * 0.0005
      particlesMesh.rotation.y += mouseX * 0.0005
  
      renderer.render(scene, camera)
    }
  
    animate()
  }
  
  // Header scroll effect
  function initHeaderScroll() {
    const header = document.querySelector("header")
  
    window.addEventListener("scroll", () => {
      if (window.scrollY > 50) {
        header.classList.add("scrolled")
      } else {
        header.classList.remove("scrolled")
      }
    })
  }
  
  // Back to top button
  function initBackToTop() {
    const backToTopBtn = document.querySelector(".back-to-top")
  
    window.addEventListener("scroll", () => {
      if (window.scrollY > 300) {
        backToTopBtn.classList.add("active")
      } else {
        backToTopBtn.classList.remove("active")
      }
    })
  
    backToTopBtn.addEventListener("click", (e) => {
      e.preventDefault()
      window.scrollTo({ top: 0, behavior: "smooth" })
    })
  }
  
  // Search and filter functionality
  function initSearchAndFilter() {
    const searchInput = document.getElementById("searchInput")
    const categoryFilter = document.getElementById("categoryFilter")
    const searchBtn = document.getElementById("searchBtn")
    const eventCards = document.querySelectorAll(".event-grid > div")
  
    // Search function
    function filterEvents() {
      const searchTerm = searchInput.value.toLowerCase()
      const category = categoryFilter.value
  
      eventCards.forEach((card) => {
        const title = card.querySelector("h3").textContent.toLowerCase()
        const cardCategory = card.getAttribute("data-category")
  
        const matchesSearch = title.includes(searchTerm)
        const matchesCategory = category === "all" || cardCategory === category
  
        if (matchesSearch && matchesCategory) {
          card.style.display = "block"
        } else {
          card.style.display = "none"
        }
      })
    }
  
    // Event listeners
    searchBtn.addEventListener("click", filterEvents)
  
    searchInput.addEventListener("keyup", (e) => {
      if (e.key === "Enter") {
        filterEvents()
      }
    })
  
    categoryFilter.addEventListener("change", filterEvents)
  }
  
  // Parallax effects
  function initParallaxEffects() {
    // Parallax scrolling effect
    window.addEventListener("scroll", () => {
      const parallaxSection = document.querySelector(".parallax-section")
      const scrollPosition = window.pageYOffset
  
      if (parallaxSection) {
        parallaxSection.style.backgroundPositionY = scrollPosition * 0.5 + "px"
      }
  
      // Parallax zoom effect for party section
      const partySection = document.querySelector(".party-section")
  
      if (partySection) {
        const partySectionTop = partySection.offsetTop
        const partySectionHeight = partySection.offsetHeight
        const viewportHeight = window.innerHeight
  
        if (scrollPosition > partySectionTop - viewportHeight && scrollPosition < partySectionTop + partySectionHeight) {
          const scale = 1 + (scrollPosition - (partySectionTop - viewportHeight)) * 0.0005
          document.querySelector(".zoom-parallax").style.transform = `scale(${Math.min(scale, 1.1)})`
        }
      }
    })
  }
  
  // Form validation
  function initFormValidation() {
    const contactForm = document.getElementById("contactForm")
    const newsletterForm = document.querySelector(".newsletter-form")
  
    if (contactForm) {
      contactForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        // Simple validation
        let isValid = true
        const inputs = contactForm.querySelectorAll("input, textarea")
  
        inputs.forEach((input) => {
          if (input.hasAttribute("required") && !input.value.trim()) {
            isValid = false
            input.classList.add("is-invalid")
          } else {
            input.classList.remove("is-invalid")
          }
        })
  
        if (isValid) {
          // Simulate form submission
          const submitBtn = contactForm.querySelector('button[type="submit"]')
          const originalText = submitBtn.textContent
  
          submitBtn.disabled = true
          submitBtn.innerHTML =
            '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...'
  
          setTimeout(() => {
            contactForm.reset()
            submitBtn.disabled = false
            submitBtn.textContent = originalText
  
            // Show success message
            const successMessage = document.createElement("div")
            successMessage.className = "alert alert-success mt-3"
            successMessage.textContent = "Your message has been sent successfully!"
            contactForm.appendChild(successMessage)
  
            setTimeout(() => {
              successMessage.remove()
            }, 3000)
          }, 1500)
        }
      })
    }
  
    if (newsletterForm) {
      newsletterForm.addEventListener("submit", (e) => {
        e.preventDefault()
  
        const emailInput = newsletterForm.querySelector('input[type="email"]')
        const submitBtn = newsletterForm.querySelector('button[type="submit"]')
  
        if (emailInput.value.trim() === "") {
          emailInput.classList.add("is-invalid")
          return
        }
  
        // Simulate subscription
        const originalText = submitBtn.textContent
        submitBtn.disabled = true
        submitBtn.innerHTML =
          '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Subscribing...'
  
        setTimeout(() => {
          newsletterForm.reset()
          submitBtn.disabled = false
          submitBtn.textContent = originalText
  
          // Show success message
          const formGroup = newsletterForm.querySelector(".input-group")
          const successMessage = document.createElement("div")
          successMessage.className = "alert alert-success mt-2"
          successMessage.textContent = "Thank you for subscribing to our newsletter!"
          formGroup.insertAdjacentElement("afterend", successMessage)
  
          setTimeout(() => {
            successMessage.remove()
          }, 3000)
        }, 1500)
      })
    }
  }
  
//   import * as THREE from "three"
  
  