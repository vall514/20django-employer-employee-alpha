// Main script file for Employer-Employee Management System

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle for the navbar
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function() {
            const mobileMenu = document.getElementById('mobile-menu');
            mobileMenu.classList.toggle('hidden');
        });
    }

    // Dropdown functionality
    const dropdownButtons = document.querySelectorAll('[data-dropdown-toggle]');
    dropdownButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-dropdown-toggle');
            const dropdown = document.getElementById(targetId);
            
            // Toggle the dropdown
            dropdown.classList.toggle('hidden');
            
            // Position the dropdown
            const buttonRect = this.getBoundingClientRect();
            dropdown.style.top = buttonRect.bottom + 'px';
            dropdown.style.left = buttonRect.left + 'px';
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        if (!event.target.closest('[data-dropdown-toggle]')) {
            const dropdowns = document.querySelectorAll('[role="dropdown"]');
            dropdowns.forEach(dropdown => {
                if (!dropdown.classList.contains('hidden')) {
                    dropdown.classList.add('hidden');
                }
            });
        }
    });

    // Form validation with custom styling
    const forms = document.querySelectorAll('[data-validate-form]');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            let isValid = true;
            
            // Validate required fields
            const requiredInputs = form.querySelectorAll('[required]');
            requiredInputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('border-danger');
                    input.classList.remove('border-gray-300');
                    
                    // Add error message if not already present
                    let errorMessage = input.nextElementSibling;
                    if (!errorMessage || !errorMessage.classList.contains('error-message')) {
                        errorMessage = document.createElement('p');
                        errorMessage.classList.add('text-danger', 'text-sm', 'mt-1', 'error-message');
                        errorMessage.innerText = 'This field is required';
                        input.parentNode.insertBefore(errorMessage, input.nextSibling);
                    }
                } else {
                    input.classList.remove('border-danger');
                    input.classList.add('border-gray-300');
                    
                    // Remove any existing error message
                    const errorMessage = input.nextElementSibling;
                    if (errorMessage && errorMessage.classList.contains('error-message')) {
                        errorMessage.remove();
                    }
                }
            });
            
            if (!isValid) {
                event.preventDefault();
                event.stopPropagation();
            }
        });
    });

    // Auto-dismiss alerts
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.classList.add('opacity-0');
            setTimeout(() => {
                alert.remove();
            }, 300);
        }, 5000);
    });

    // Tab system
    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabGroup = this.closest('[role="tablist"]');
            const targetId = this.getAttribute('data-tab-target');
            
            // Hide all tab contents
            const tabContents = document.querySelectorAll('[role="tabpanel"]');
            tabContents.forEach(content => {
                content.classList.add('hidden');
            });
            
            // Show the target tab content
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.remove('hidden');
            }
            
            // Update active state of tabs
            const tabs = tabGroup.querySelectorAll('.tab-button');
            tabs.forEach(tab => {
                tab.classList.remove('tab-active', 'border-primary', 'text-primary');
                tab.classList.add('border-transparent', 'text-gray-500');
            });
            
            this.classList.add('tab-active', 'border-primary', 'text-primary');
            this.classList.remove('border-transparent', 'text-gray-500');
        });
    });
});
