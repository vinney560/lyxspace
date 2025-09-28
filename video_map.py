VIDEO_MAP = {
    #Course Id, Module Id, Lesson Id
    
    # Ubuntu & Linux Mastery (course_id=1)
    (1, 1, 1): 'kPylihJRG70',  # Linux Fundamentals & Installation, Lesson 1
    (1, 1, 2): '7Zt2Mp2IeBI',  # Linux Fundamentals & Installation, Lesson 2
    (1, 2, 1): 'uwAqEzhyjtw',  # Command Line Mastery, Lesson 1
    (1, 2, 2): 'Jfvg3CS1X3A',  # Command Line Mastery, Lesson 2
    (1, 2, 3): 'QBWX_4ho8D4',  # Command Line Mastery, Lesson 3
    (1, 3, 1): 'MBBWVgE0ewk',  # File System & Permissions, Lesson 1
    (1, 3, 2): '7ABkcHLdG_A',  # File System & Permissions, Lesson 2
    (1, 3, 3): 'LHhPvq5R0hA',  # File System & Permissions, Lesson 3
    (1, 3, 4): 'ODk8CoSLofA',  # File System & Permissions, Lesson 4
    (1, 3, 5): 'HbgzrKJvDRw',  # File System & Permissions, Lesson 5
    (1, 3, 6): 'dzHscTzpAME',  # File System & Permissions, Lesson 6
    (1, 4, 1): '19WOD84JFxA',  # User & Process Management, Lesson 1
    (1, 4, 2): 'B832XYN46UM',  # User & Process Management, Lesson 2
    (1, 5, 1): 'lYvijnPI1Rg',  # Networking & Security, Lesson 1
    (1, 5, 2): '_IOZ8_cPgu8',  # Networking & Security, Lesson 2
    (1, 5, 3): 'SK8D1bdJh7s',  # Networking & Security, Lesson 3
    (1, 6, 1): 'om7Hrrr6wsk',  # Shell Scripting & Automation, Lesson 1
    (1, 6, 2): 'usyzSMFfUTg',  # Shell Scripting & Automation, Lesson 2
    (1, 6, 3): 'cQepf9fY6cE',  # Shell Scripting & Automation, Lesson 3

    # Linux Server Administration (course_id=2)
    (2, 1, 1): 'RgKAFK5djSk',  # Server Setup & Configuration, Lesson 1
    (2, 2, 1): 'OPf0YbXqDm0',  # Service Management (Systemd), Lesson 1
    (2, 3, 1): '2Vv-BfVoq4g',  # Security Hardening & Firewalls, Lesson 1
    (2, 4, 1): 'CevxZvSJLk8',  # Performance Monitoring & Tuning, Lesson 1
    (2, 5, 1): 'YQHsXMglC9A',  # Containerization with Docker, Lesson 1
    (2, 6, 1): 'hT_nvWreIhg',  # Enterprise Deployment Strategies, Lesson 1

    # Bash Shell Scripting Mastery (course_id=3)
    (3, 1, 1): 'ktvTqknDobU',  # Bash Fundamentals, Lesson 1
    (3, 2, 1): 'pRpeEdMmmQ0',  # Variables & Control Structures, Lesson 1
    (3, 3, 1): 'uelHwf8o7_U',  # Functions & Advanced Scripting, Lesson 1
    (3, 4, 1): 'YqeW9_5kURI',  # System Automation & Scheduling, Lesson 1
    (3, 5, 1): '60ItHLz5WEA',  # Real-world Scripting Projects, Lesson 1

    # HTML5 & CSS3 Fundamentals (course_id=4)
    (4, 1, 1): 'CwfoyVa980U',  # HTML5 Basics & Semantic Elements, Lesson 1
    (4, 2, 1): 'E07s5ZYygMg',  # CSS3 Fundamentals & Styling, Lesson 1
    (4, 3, 1): 'M7lc1UVf-VE',  # Layouts & Positioning Techniques, Lesson 1
    (4, 4, 1): 'aqz-KE-bpKQ',  # Responsive Design & Media Queries, Lesson 1
    (4, 5, 1): 'dQw4w9WgXcQ',  # Advanced CSS Features & Animations, Lesson 1

    # Responsive Web Design (course_id=5)
    (5, 1, 1): '9bZkp7q19f0',  # CSS Grid Mastery, Lesson 1
    (5, 2, 1): '3JZ_D3ELwOQ',  # Flexbox Techniques & Layouts, Lesson 1
    (5, 3, 1): 'e-ORhEE9VVg',  # Responsive Frameworks (Bootstrap), Lesson 1
    (5, 4, 1): 'L_jWHffIx5E',  # Advanced Responsive Patterns, Lesson 1

    # Advanced CSS & Sass (course_id=6)
    (6, 1, 1): 'fJ9rUzIMcZQ',  # Sass Fundamentals & Mixins, Lesson 1
    (6, 2, 1): 'kJQP7kiw5Fk',  # CSS Architecture & Methodologies, Lesson 1
    (6, 3, 1): 'RgKAFK5djSk',  # Advanced Animations & Transitions, Lesson 1
    (6, 4, 1): 'OPf0YbXqDm0',  # Performance Optimization, Lesson 1

    # JavaScript Programming (course_id=7)
    (7, 1, 1): '2Vv-BfVoq4g',  # JavaScript Basics & Fundamentals, Lesson 1
    (7, 2, 1): 'CevxZvSJLk8',  # DOM Manipulation & Events, Lesson 1
    (7, 3, 1): 'YQHsXMglC9A',  # Advanced JavaScript Concepts, Lesson 1
    (7, 4, 1): 'hT_nvWreIhg',  # Async Programming & APIs, Lesson 1
    (7, 5, 1): 'ktvTqknDobU',  # Modern Frameworks Overview, Lesson 1
    (7, 6, 1): 'pRpeEdMmmQ0',  # Project Development & Best Practices, Lesson 1

    # React.js Development (course_id=8)
    (8, 1, 1): 'uelHwf8o7_U',  # React Fundamentals & JSX, Lesson 1
    (8, 2, 1): 'YqeW9_5kURI',  # Components & Props, Lesson 1
    (8, 3, 1): '60ItHLz5WEA',  # State Management & Hooks, Lesson 1
    (8, 4, 1): 'CwfoyVa980U',  # Routing & API Integration, Lesson 1
    (8, 5, 1): 'E07s5ZYygMg',  # Advanced Patterns & Performance, Lesson 1
    (8, 6, 1): 'M7lc1UVf-VE',  # Testing & Deployment, Lesson 1

    # Node.js Backend Development (course_id=9)
    (9, 1, 1): 'aqz-KE-bpKQ',  # Node.js Fundamentals, Lesson 1
    (9, 2, 1): 'dQw4w9WgXcQ',  # Express.js & Middleware, Lesson 1
    (9, 3, 1): '9bZkp7q19f0',  # Database Integration, Lesson 1
    (9, 4, 1): '3JZ_D3ELwOQ',  # Authentication & Security, Lesson 1
    (9, 5, 1): 'e-ORhEE9VVg',  # API Development & Deployment, Lesson 1

    # Python Development (course_id=10)
    (10, 1, 1): 'L_jWHffIx5E',  # Python Fundamentals, Lesson 1
    (10, 2, 1): 'fJ9rUzIMcZQ',  # Data Structures & Algorithms, Lesson 1
    (10, 3, 1): 'kJQP7kiw5Fk',  # Web Development with Flask, Lesson 1
    (10, 4, 1): 'RgKAFK5djSk',  # Data Science & Analysis, Lesson 1
    (10, 5, 1): 'OPf0YbXqDm0',  # Automation & Scripting, Lesson 1
    (10, 6, 1): '2Vv-BfVoq4g',  # Advanced Python Topics, Lesson 1
    (10, 7, 1): 'CevxZvSJLk8',  # Capstone Project, Lesson 1

    # Flask Web Framework (course_id=11)
    (11, 1, 1): 'YQHsXMglC9A',  # Django Fundamentals & Setup, Lesson 1
    (11, 2, 1): 'hT_nvWreIhg',  # Models & Database Design, Lesson 1
    (11, 3, 1): 'ktvTqknDobU',  # Views & URL Routing, Lesson 1
    (11, 4, 1): 'pRpeEdMmmQ0',  # Templates & Frontend Integration, Lesson 1
    (11, 5, 1): 'uelHwf8o7_U',  # Forms & User Input, Lesson 1
    (11, 6, 1): 'YqeW9_5kURI',  # Authentication & Deployment, Lesson 1

    # Python for Data Science (course_id=12)
    (12, 1, 1): '60ItHLz5WEA',  # Python for Data Analysis, Lesson 1
    (12, 2, 1): 'CwfoyVa980U',  # Pandas & Data Manipulation, Lesson 1
    (12, 3, 1): 'E07s5ZYygMg',  # Data Visualization, Lesson 1
    (12, 4, 1): 'M7lc1UVf-VE',  # Statistical Analysis, Lesson 1
    (12, 5, 1): 'aqz-KE-bpKQ',  # Machine Learning Fundamentals, Lesson 1
    (12, 6, 1): 'dQw4w9WgXcQ',  # Real-world Data Projects, Lesson 1

    # Automation with Python (course_id=13)
    (13, 1, 1): '9bZkp7q19f0',  # Python Scripting Basics, Lesson 1
    (13, 2, 1): '3JZ_D3ELwOQ',  # File & System Automation, Lesson 1
    (13, 3, 1): 'e-ORhEE9VVg',  # Web Automation & Scraping, Lesson 1
    (13, 4, 1): 'L_jWHffIx5E',  # API Automation & Integration, Lesson 1
}