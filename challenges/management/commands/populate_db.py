from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from challenges.models import Category, Challenge, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from partnerships.models import PartnershipRequest
from accounts.models import Activity

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with demo categories, users (all 4 roles), challenges, solutions, projects, and partnerships."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Initializing database population for CivicConnect..."))

        # 1. Categories
        categories_data = [
            ("Environment", "environment", "bi-tree-fill", "Conservation, biodiversity, reforestation, and ecological preservation."),
            ("Education", "education", "bi-mortarboard-fill", "Accessible learning, literacy initiatives, digital classrooms, and skill enhancement."),
            ("Healthcare", "healthcare", "bi-heart-pulse-fill", "Community health clinics, medical access, epidemic detection, and maternal wellness."),
            ("Agriculture", "agriculture", "bi-flower1", "Sustainable crop cultivation, post-harvest preservation, and water-efficient irrigation."),
            ("Transportation", "transportation", "bi-bus-front-fill", "Green transit, pedestrian safety, urban congestion, and rural connectivity."),
            ("Public Safety", "public-safety", "bi-shield-check", "Disaster mitigation, early flood alerts, emergency response, and municipal security."),
            ("Waste Management", "waste-management", "bi-recycle", "Circular economy, plastics recycling, organic waste recovery, and electronic waste handling."),
            ("Rural Development", "rural-development", "bi-house-heart-fill", "Electrification, clean drinking water, sanitation facilities, and rural livelihoods."),
            ("Technology and Innovation", "technology-and-innovation", "bi-cpu-fill", "Open hardware, IoT sensors, AI for social impact, and renewable energy grids."),
        ]

        categories = {}
        for name, slug, icon, desc in categories_data:
            cat, created = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'icon': icon, 'description': desc}
            )
            categories[slug] = cat
        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(categories)} categories."))

        # 2. Users (Student, University, Industry, Admin)
        users_data = [
            # Superuser / Admin
            ("admin", "admin@civicconnect.org", "admin123", "Super", "Admin", "admin", "CivicConnect Foundation", "Global Operations", "Platform superuser and chief administrator overseeing civic challenge approvals."),
            # Universities
            ("univ_mit", "innovation@mit.edu", "mit123", "MIT", "Innovation Lab", "university", "Massachusetts Institute of Technology", "Cambridge, MA, USA", "Interdisciplinary academic research lab working on energy, climate, and student venture mentorship."),
            ("univ_stanford", "socialimpact@stanford.edu", "stanford123", "Stanford", "Impact Center", "university", "Stanford University", "Stanford, CA, USA", "Dedicated university center connecting faculty expertise with scalable community challenges."),
            ("univ_iit", "ruraltech@iitb.ac.in", "iit123", "IIT", "Bombay CTARA", "university", "Indian Institute of Technology Bombay", "Mumbai, Maharashtra, India", "Center for Technology Alternatives for Rural Areas focusing on grassroots engineering solutions."),
            # Industries
            ("ind_greenpower", "contact@greenpower.io", "green123", "GreenPower", "Solutions", "industry", "GreenPower Energy Systems", "Chicago, IL, USA", "Renewable energy corporation investing CSR and technical capital into rural clean energy innovations."),
            ("ind_techcorp", "rnd@apextech.com", "tech123", "Apex", "Technologies", "industry", "Apex Technologies Global", "San Jose, CA, USA", "Enterprise technology provider supporting open hardware and computer vision for societal betterment."),
            ("ind_agrisolutions", "partnerships@agrigrow.org", "agri123", "AgriGrow", "Enterprises", "industry", "AgriGrow Sustainable Hardware", "Pune, Maharashtra, India", "Agricultural machinery firm co-developing modular post-harvest storage systems for farmers."),
            # Students / Citizens
            ("student_alex", "alex.chen@mit.edu", "alex123", "Alex", "Chen", "student", "MIT Engineering", "Boston, MA, USA", "Undergraduate mechanical engineering student passionate about distributed solar refrigeration."),
            ("student_priya", "priya.sharma@students.ac.in", "priya123", "Priya", "Sharma", "student", "IIT Bombay", "Mumbai, India", "Computer science researcher specializing in embedded edge AI and computer vision models."),
            ("citizen_john", "john.miller@communityaction.org", "john123", "John", "Miller", "student", "Tampa Bay Baykeeper NGO", "Tampa, FL, USA", "Civic community advocate monitoring marine plastic pollution and urban storm runoffs."),
            ("citizen_fatima", "fatima.hassan@ruralhealth.org", "fatima123", "Fatima", "Al-Hassan", "student", "Nairobi Health Coalition", "Nairobi, Kenya", "Community nurse advocating for portable rural diagnostic and telemedicine kits."),
        ]

        users = {}
        for uname, email, pwd, fname, lname, role, inst, loc, bio in users_data:
            user = User.objects.filter(username=uname).first()
            if not user:
                if role == 'admin':
                    user = User.objects.create_superuser(
                        username=uname, email=email, password=pwd,
                        first_name=fname, last_name=lname, role=role,
                        institution_name=inst, location=loc, bio=bio
                    )
                else:
                    user = User.objects.create_user(
                        username=uname, email=email, password=pwd,
                        first_name=fname, last_name=lname, role=role,
                        institution_name=inst, location=loc, bio=bio
                    )
            users[uname] = user

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(users)} users across all 4 roles."))

        # 3. Societal Challenges
        challenges_data = [
            {
                "key": "cold_storage",
                "title": "Affordable Solar-Powered Cold Storage for Perishable Smallholder Harvests",
                "category": categories["agriculture"],
                "creator": users["univ_iit"],
                "location": "Nashik & Pune Rural District, Maharashtra, India",
                "severity": "critical",
                "status": "in_progress",
                "organization_name": "IIT Bombay Rural Technology Cell",
                "description": (
                    "Over 30% of perishable tomatoes, onions, and leafy vegetables rot before reaching mandis due to lack of localized cold storage.\n\n"
                    "High grid electricity tariffs and frequent power outages make conventional refrigeration uneconomical for smallholder farmers owning under 2 acres.\n\n"
                    "Farmers require a decentralized, passive or solar-hybrid cooling unit that costs less than $1,000 and operates reliably without relying on uninterrupted electrical grid access."
                ),
                "expected_impact": (
                    "1. Eliminate 80% of immediate harvest spoilage for over 500 farmer families.\n"
                    "2. Increase average seasonal household income by 25-35% through extended price negotiation window.\n"
                    "3. Prevent localized food waste while serving as an open design for agricultural co-ops across South Asia and East Africa."
                ),
            },
            {
                "key": "waste_sorting",
                "title": "Autonomous Municipal Waste Sorting Using Low-Cost Edge AI & Robotics",
                "category": categories["waste-management"],
                "creator": users["citizen_john"],
                "location": "Austin & San Antonio Municipal Areas, Texas, USA",
                "severity": "high",
                "status": "in_progress",
                "organization_name": "Texas Clean Rivers Alliance",
                "description": (
                    "Municipal recycling sorting facilities currently discard more than 40% of recyclable plastics and aluminum into landfills due to manual contamination sorting bottlenecks.\n\n"
                    "Recyclable materials are mixed with organic and dangerous hazardous items, exposing sanitation personnel to health hazards.\n\n"
                    "We need an open, cost-effective sorting system using computer vision capable of real-time classification at 60 items per minute."
                ),
                "expected_impact": (
                    "1. Increase automated recycling throughput from 55% to 88% in municipal sorting facilities.\n"
                    "2. Protect sanitation team members from chemical and sharp hazard handling.\n"
                    "3. Divert approximately 1,200 tons of reusable high-density polymers from landfills each year."
                ),
            },
            {
                "key": "microplastics",
                "title": "Combating Microplastic Runoff in Coastal Fishery Estuaries",
                "category": categories["environment"],
                "creator": users["citizen_john"],
                "location": "Tampa Bay Estuary, Florida, USA",
                "severity": "high",
                "status": "approved",
                "organization_name": "Coastal Marine Conservation Forum",
                "description": (
                    "Stormwater discharge carries tire wear particles, synthetic textile fibers, and broken polymers straight into juvenile fish nursery zones.\n\n"
                    "Local commercial fishing cooperatives report declining shellfish populations and detectable synthetic residue in commercial oyster beds.\n\n"
                    "Seeking modular, passive bio-filtration barriers that can be installed at stormwater culverts without obstructing storm drainage."
                ),
                "expected_impact": (
                    "1. Trap 75% of particulate plastics above 50 microns at 12 primary coastal drainage discharge points.\n"
                    "2. Restore healthy shellfish breeding conditions in 40 square kilometers of estuary.\n"
                    "3. Provide municipal environmental boards with a low-cost, bio-degradable filtration template."
                ),
            },
            {
                "key": "rural_telemedicine",
                "title": "Solar-Assisted Diagnostic Telemedicine Backpack for Remote Clinics",
                "category": categories["healthcare"],
                "creator": users["citizen_fatima"],
                "location": "Turkana & Marsabit Counties, Northern Kenya",
                "severity": "critical",
                "status": "in_progress",
                "organization_name": "Rural Health Outreach Alliance",
                "description": (
                    "Expectant mothers and elders in arid pastoral communities must travel over 40 kilometers through unpaved roads to reach basic diagnostic facilities.\n\n"
                    "Health workers lack portable ultrasound, ECG, and blood biochemistry analyzers capable of functioning in dusty environments with no cell connectivity.\n\n"
                    "We need a rugged, portable diagnostics backpack that logs vital readings locally and synchronizes securely with district hospitals whenever cellular signal is reached."
                ),
                "expected_impact": (
                    "1. Enable early triage for prenatal complications across 25 remote pastoral villages.\n"
                    "2. Reduce maternal mortality by an estimated 35% through proactive hospital referral.\n"
                    "3. Equip 50 community health volunteers with digital diagnostic tools."
                ),
            },
            {
                "key": "tribal_education",
                "title": "Solar-Powered Offline Digital Classrooms for Remote Tribal Schools",
                "category": categories["education"],
                "creator": users["univ_stanford"],
                "location": "Bastar District, Chhattisgarh, India",
                "severity": "high",
                "status": "approved",
                "organization_name": "Stanford Learning Outreach Foundation",
                "description": (
                    "Government primary schools in remote forested districts experience chronic internet blackouts and erratic grid power, locking children out of modern educational media.\n\n"
                    "Teachers lack audio-visual tools in native dialects (Gondi and Halbi) to reinforce STEM basics and foundational literacy.\n\n"
                    "We seek a low-power single-board computer hub powered by a mini solar panel that serves localized offline interactive modules via local Wi-Fi to refurbished tablets."
                ),
                "expected_impact": (
                    "1. Empower 2,400 elementary students with interactive mathematics and multilingual science modules.\n"
                    "2. Bridge digital literacy gap without incurring monthly recurring data subscription costs.\n"
                    "3. Zero grid power required; 100% solar self-sufficiency."
                ),
            },
            {
                "key": "flood_warning",
                "title": "Community-Mesh IoT Early Warning Sensor Network for Urban Flash Floods",
                "category": categories["public-safety"],
                "creator": users["student_priya"],
                "location": "Metro Manila River Basin, Philippines",
                "severity": "high",
                "status": "approved",
                "organization_name": "Disaster Resilience Youth Circle",
                "description": (
                    "Typhoon season causes rapid inundation in low-lying informal settlements within 20 minutes of torrential rainfall.\n\n"
                    "Centralized weather radar misses micro-basin river surge events, and sirens often activate too late for families to safely evacuate ground-floor belongings.\n\n"
                    "Seeking low-cost ultrasonic water level sensors linked via LoRa wireless mesh that broadcast SMS and audio alerts directly to barangay council halls."
                ),
                "expected_impact": (
                    "1. Provide a reliable 30-to-45-minute advance flood surge evacuation window.\n"
                    "2. Protect more than 15,000 residents across 6 vulnerable riverbank barangays.\n"
                    "3. Total hardware node cost kept below $35 per sensing station."
                ),
            },
            {
                "key": "water_sensor_mesh",
                "title": "Open-Source Water Quality Sensor Mesh for Urban Rivers and Canals",
                "category": categories["technology-and-innovation"],
                "creator": users["student_alex"],
                "location": "Chicago River & Industrial Corridors, Illinois, USA",
                "severity": "medium",
                "status": "pending",  # Specifically PENDING to demonstrate Admin 1-Click Approval!
                "organization_name": "Urban Waterway Guardians",
                "description": (
                    "Industrial runoff events often take place during weekend evenings when municipal environmental compliance inspectors are off duty.\n\n"
                    "Citizen volunteers lack calibrated dissolved oxygen (DO), turbidity, and pH sensing units that can stream open telemetry to public dashboards.\n\n"
                    "Proposing open-hardware floating buoys that stream continuous water telemetry to public IPFS and open-data civic dashboards."
                ),
                "expected_impact": (
                    "1. 24/7 continuous water quality monitoring across 15 miles of urban waterway.\n"
                    "2. Immediate public notification within 3 minutes of toxic chemical or sewage discharge spikes.\n"
                    "3. Open database accessible to university researchers and environmental policy makers."
                ),
            },
        ]

        challenges = {}
        for cdata in challenges_data:
            ch, created = Challenge.objects.get_or_create(
                title=cdata["title"],
                defaults={
                    "category": cdata["category"],
                    "creator": cdata["creator"],
                    "location": cdata["location"],
                    "problem_severity": cdata["severity"],
                    "status": cdata["status"],
                    "organization_name": cdata["organization_name"],
                    "description": cdata["description"],
                    "expected_impact": cdata["expected_impact"],
                }
            )
            challenges[cdata["key"]] = ch

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(challenges)} societal challenges."))

        # 4. Proposed Solutions
        solutions_data = [
            {
                "key": "cold_storage_sol",
                "challenge": challenges["cold_storage"],
                "creator": users["student_alex"],
                "title": "Modular Peltier-Thermoelectric Cold Room with Phase-Change Thermal Battery",
                "estimated_duration": "4 Months",
                "is_accepted": True,
                "description": (
                    "A hybrid cooling chamber utilizing solid-state thermoelectric coolers paired with an eco-friendly phase change material (PCM) brine tank.\n\n"
                    "During peak daytime sunlight, a 600W solar panel array charges the thermal battery by freezing the PCM solution. During nighttime, the PCM maintains chamber temperature between 4°C and 8°C without drawing battery power."
                ),
                "proposed_implementation": (
                    "Phase 1 (Month 1): Thermal modeling and PCM container enclosure fabrication using local PUF insulated panels.\n"
                    "Phase 2 (Month 2): Solar MPPT charge controller integration and digital IoT temperature datalogger installation.\n"
                    "Phase 3 (Month 3): Laboratory load testing with 500 kg of fresh tomatoes and green chili.\n"
                    "Phase 4 (Month 4): Field deployment at a farmer cooperative in Nashik, Maharashtra."
                ),
                "expected_outcome": (
                    "Maintain uninterrupted 4°C - 8°C cooling for 48 hours without grid power.\n"
                    "Extend tomato shelf life from 3 days to 21 days.\n"
                    "Total manufacturing bill of materials under $850."
                ),
                "required_resources": "6x 100W Monocrystalline panels, 4x TEC1-12715 Peltier modules, food-grade thermal phase change salt solution, ESP32 temperature logger, local metal fabricator."
            },
            {
                "key": "waste_sorting_sol",
                "challenge": challenges["waste_sorting"],
                "creator": users["student_priya"],
                "title": "Edge AI YOLOv8 Vision Sorter with High-Speed Pneumatic Jet Diverters",
                "estimated_duration": "12 Weeks",
                "is_accepted": True,
                "description": (
                    "An industrial conveyor attachment featuring an NVIDIA Jetson Orin Nano running a lightweight fine-tuned YOLOv8 classification model.\n\n"
                    "High-resolution cameras capture items entering the chute at 1.5 m/s, classifies plastic types (PET, HDPE, PP) and aluminum cans, and triggers precision solenoid air valves to blow items into respective collector bins."
                ),
                "proposed_implementation": (
                    "Step 1: Dataset collection of 10,000 crushed and dirty consumer containers.\n"
                    "Step 2: Train quantized TensorRT vision model operating under 12ms inference latency.\n"
                    "Step 3: Fabricate 8-valve pneumatic ejection manifold with air compressor regulator.\n"
                    "Step 4: Bench testing on experimental municipal sorting line."
                ),
                "expected_outcome": (
                    "Achieve 94.2% classification accuracy at 75 items per minute throughput.\n"
                    "Reduce sorting line labor contamination hazards by 90%.\n"
                    "Complete open-source CAD design and weights release on GitHub."
                ),
                "required_resources": "NVIDIA Jetson Nano, Basler industrial USB3 camera, 8-channel relay board, pneumatic solenoid valves, 50L air compressor."
            },
            {
                "key": "telemed_kit_sol",
                "challenge": challenges["rural_telemedicine"],
                "creator": users["citizen_fatima"],
                "title": "Rugged Telemedicine Backpack with Offline Encrypted SQLite Medical Vault",
                "estimated_duration": "3 Months",
                "is_accepted": True,
                "description": (
                    "A field-tested solar-charged backpack containing wireless ultrasound probe, pulse oximeter, glucometer, and a ruggedized Android tablet running offline clinical triage software.\n\n"
                    "Data is stored in local encrypted databases and opportunistically synchronized with the Ministry of Health cloud when nurses enter cellular transmission range."
                ),
                "proposed_implementation": (
                    "Month 1: Hardware integration inside dust-tight IP67 Pelican case with flexible 40W solar panel.\n"
                    "Month 2: Clinical workflow software translation into Swahili and Turkana.\n"
                    "Month 3: Pilot training with 15 community healthcare workers in Turkana County."
                ),
                "expected_outcome": (
                    "Perform 1,500 remote diagnostic prenatal checkups annually.\n"
                    "Detect high-risk ectopic pregnancies and gestational diabetes weeks in advance."
                ),
                "required_resources": "Handheld USB ultrasound probe, Android tablet, 40W folding solar panel, IP67 enclosure, medical ethics advisory."
            },
            {
                "key": "microplastic_sol",
                "challenge": challenges["microplastics"],
                "creator": users["student_alex"],
                "title": "Bio-Composite Coconut Husk & Chitosan Stormwater Culvert Filter Screen",
                "estimated_duration": "8 Weeks",
                "is_accepted": False,
                "description": (
                    "A biodegradable filter cartridge crafted from pressed coir (coconut fibers) impregnated with marine-safe chitosan biopolymers that electrostatically attract microplastic beads and tire residue."
                ),
                "proposed_implementation": "Construct modular wire mesh frames that fit inside standard municipal storm drains with overflow bypass protection during hurricanes.",
                "expected_outcome": "Capture up to 68% of synthetic microfibers before estuary entry without impeding hydraulic flow.",
                "required_resources": "Coir fiber rolls, food-grade chitosan powder, stainless steel bracket mounts."
            }
        ]

        solutions = {}
        for sdata in solutions_data:
            sol, created = Solution.objects.get_or_create(
                title=sdata["title"],
                challenge=sdata["challenge"],
                defaults={
                    "creator": sdata["creator"],
                    "estimated_duration": sdata["estimated_duration"],
                    "is_accepted": sdata["is_accepted"],
                    "description": sdata["description"],
                    "proposed_implementation": sdata["proposed_implementation"],
                    "expected_outcome": sdata["expected_outcome"],
                    "required_resources": sdata["required_resources"],
                }
            )
            solutions[sdata["key"]] = sol

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(solutions)} proposed solutions."))

        # 5. Collaborative Projects
        projects_data = [
            {
                "key": "cold_storage_project",
                "title": "Solar Cold Storage Prototype Pilot - Maharashtra Field Deployment",
                "challenge": challenges["cold_storage"],
                "solution": solutions["cold_storage_sol"],
                "lead": users["student_alex"],
                "status": "active",
                "progress_percentage": 65,
                "start_date": date.today() - timedelta(days=45),
                "expected_completion_date": date.today() + timedelta(days=75),
                "description": (
                    "Multi-institutional initiative uniting student innovators from MIT, faculty engineering supervisors at IIT Bombay, and manufacturing experts at AgriGrow Enterprises.\n\n"
                    "Goal: Fabricate 2 operational 500kg solar cold-rooms and conduct real-world shelf-life validation with the Nashik Farmers Producer Organization."
                ),
                "members": [
                    (users["student_alex"], "Project Lead"),
                    (users["univ_iit"], "Faculty Mentor"),
                    (users["ind_agrisolutions"], "Industry Advisor"),
                    (users["student_priya"], "Student Researcher"),
                ]
            },
            {
                "key": "waste_sorting_project",
                "title": "AI Robotic Sorter Field Trial - Municipal Facility Deployment",
                "challenge": challenges["waste_sorting"],
                "solution": solutions["waste_sorting_sol"],
                "lead": users["student_priya"],
                "status": "active",
                "progress_percentage": 40,
                "start_date": date.today() - timedelta(days=30),
                "expected_completion_date": date.today() + timedelta(days=90),
                "description": (
                    "Partnership between Stanford University's robotics laboratory, student AI developers, and Apex Technologies R&D.\n\n"
                    "Deploying a high-speed vision chute at the Austin Recycling Processing Center to evaluate real-time plastic segregation accuracy under dirty municipal conditions."
                ),
                "members": [
                    (users["student_priya"], "Project Lead"),
                    (users["univ_stanford"], "Faculty Mentor"),
                    (users["ind_techcorp"], "Industry Advisor"),
                    (users["citizen_john"], "Community Representative"),
                ]
            },
            {
                "key": "telemed_project",
                "title": "Pastoral Health Telemedicine Kit Field Rollout",
                "challenge": challenges["rural_telemedicine"],
                "solution": solutions["telemed_kit_sol"],
                "lead": users["citizen_fatima"],
                "status": "planning",
                "progress_percentage": 20,
                "start_date": date.today() - timedelta(days=10),
                "expected_completion_date": date.today() + timedelta(days=120),
                "description": (
                    "Collaborative program manufacturing 20 diagnostic backpack units and conducting clinical safety verification with Kenya Health ministry mentors."
                ),
                "members": [
                    (users["citizen_fatima"], "Project Lead"),
                    (users["ind_greenpower"], "Industry Advisor"),
                    (users["student_alex"], "Hardware Engineer"),
                ]
            }
        ]

        projects = {}
        for pdata in projects_data:
            proj, created = Project.objects.get_or_create(
                title=pdata["title"],
                challenge=pdata["challenge"],
                defaults={
                    "solution": pdata["solution"],
                    "lead": pdata["lead"],
                    "status": pdata["status"],
                    "progress_percentage": pdata["progress_percentage"],
                    "start_date": pdata["start_date"],
                    "expected_completion_date": pdata["expected_completion_date"],
                    "description": pdata["description"],
                }
            )
            projects[pdata["key"]] = proj

            # Project Memberships
            for member_user, member_role in pdata["members"]:
                ProjectMembership.objects.get_or_create(
                    project=proj,
                    user=member_user,
                    defaults={"role": member_role}
                )

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(projects)} collaborative projects and team memberships."))

        # 6. Strategic Partnerships
        partnerships_data = [
            {
                "requesting": users["ind_agrisolutions"],
                "target": users["univ_iit"],
                "project": projects["cold_storage_project"],
                "challenge": challenges["cold_storage"],
                "type": "technical",
                "status": "accepted",
                "message": (
                    "AgriGrow Sustainable Hardware is eager to provide mechanical tooling, sheet metal stamping, and testing equipment for the solar cold storage initiative.\n"
                    "We would like to co-mentor student engineers and assist in industrializing the thermal insulation casing."
                ),
                "response_note": "We warmly welcome AgriGrow's manufacturing expertise and have scheduled a bi-weekly technical review with the student design team."
            },
            {
                "requesting": users["univ_stanford"],
                "target": users["ind_techcorp"],
                "project": projects["waste_sorting_project"],
                "challenge": challenges["waste_sorting"],
                "type": "mentorship",
                "status": "pending",
                "message": (
                    "Stanford Social Impact Center invites Apex Technologies senior computer vision engineers to review our edge neural network quantization and provide feedback on industrial pneumatic actuators."
                ),
                "response_note": ""
            },
            {
                "requesting": users["ind_greenpower"],
                "target": users["univ_mit"],
                "project": None,
                "challenge": challenges["microplastics"],
                "type": "general_collaboration",
                "status": "accepted",
                "message": (
                    "GreenPower would like to sponsor an academic research fellowship focused on marine microplastic interception in industrial canals."
                ),
                "response_note": "Proposal approved by the MIT Energy & Environment board. Excited to begin research collaboration."
            }
        ]

        for p_req in partnerships_data:
            PartnershipRequest.objects.get_or_create(
                requesting_organization=p_req["requesting"],
                target_organization=p_req["target"],
                challenge=p_req["challenge"],
                defaults={
                    "project": p_req["project"],
                    "partnership_type": p_req["type"],
                    "status": p_req["status"],
                    "message": p_req["message"],
                    "response_note": p_req["response_note"],
                }
            )

        self.stdout.write(self.style.SUCCESS("Created/Verified strategic partnership requests."))

        # 7. Votes & Comments
        for ch in challenges.values():
            # Upvote with different users
            for u in [users["student_alex"], users["student_priya"], users["citizen_john"], users["univ_mit"], users["ind_greenpower"]]:
                Vote.objects.get_or_create(user=u, challenge=ch)

        # Comments
        comments_data = [
            (users["univ_iit"], challenges["cold_storage"], "Our engineering department has tested passive evaporative coolers; pairing with Peltier units is a breakthrough approach for vegetable farmers!"),
            (users["ind_agrisolutions"], challenges["cold_storage"], "AgriGrow can sponsor the sheet-metal prototyping in our Pune manufacturing facility."),
            (users["student_alex"], challenges["cold_storage"], "Thanks for the feedback! We are currently benchmarking phase change salts with 6°C freezing thresholds."),
            (users["ind_techcorp"], challenges["waste_sorting"], "We recommend using FP16 quantization on the Jetson Nano to ensure sustained 60+ FPS inference without thermal throttling."),
            (users["student_priya"], challenges["waste_sorting"], "Excellent advice; TensorRT benchmark tests confirmed steady 78 FPS with our dataset!"),
            (users["citizen_john"], challenges["microplastics"], "Local oyster farmers in Tampa Bay are eager to participate in monitoring bio-filters."),
        ]

        for u, ch, text in comments_data:
            Comment.objects.get_or_create(
                user=u, challenge=ch, content=text
            )

        # 8. Activity logs
        for u in users.values():
            Activity.objects.get_or_create(
                user=u,
                title=f"Logged into CivicConnect Platform",
                defaults={"activity_type": "login", "link": "/dashboard/"}
            )

        self.stdout.write(self.style.SUCCESS("Demo database successfully populated with rich data!"))

