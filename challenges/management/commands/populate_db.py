from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta

from challenges.models import Category, Challenge, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from accounts.models import Activity

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds database with demo categories, users (1 admin, 3 organizations, 2 citizens), challenges, solutions, and projects."

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

        # 2. Users (1 Admin, 3 Organizations with each org_type, 2 Citizens)
        users_data = [
            # 1 Admin
            ("admin", "admin@civicconnect.org", "admin123", "Super", "Admin", "admin", None, "CivicConnect Foundation", "Global Operations", "Platform superuser and administrator.", True),
            # 3 Organizations (university, industry, government_ngo)
            ("univ_mit", "innovation@mit.edu", "mit123", "MIT", "Innovation Lab", "organization", "university", "Massachusetts Institute of Technology", "Cambridge, MA, USA", "Interdisciplinary academic research lab working on climate and energy mentorship.", True),
            ("ind_greenpower", "contact@greenpower.io", "green123", "GreenPower", "Solutions", "organization", "industry", "GreenPower Energy Systems", "Chicago, IL, USA", "Renewable energy corporation investing technical capital and sponsoring pilot trials.", True),
            ("ngo_baykeeper", "contact@baykeeper.org", "bay123", "Tampa Bay", "Baykeeper", "organization", "government_ngo", "Tampa Bay Baykeeper NGO", "Tampa, FL, USA", "Civic environmental coalition monitoring coastal habitats and municipal drainage.", True),
            # 2 Citizens
            ("student_alex", "alex.chen@mit.edu", "alex123", "Alex", "Chen", "citizen", None, "MIT Engineering", "Boston, MA, USA", "Mechanical engineering student passionate about distributed clean refrigeration.", True),
            ("student_priya", "priya.sharma@students.ac.in", "priya123", "Priya", "Sharma", "citizen", None, "IIT Bombay", "Mumbai, India", "Computer science researcher specializing in edge AI and computer vision models.", True),
        ]

        users = {}
        for uname, email, pwd, fname, lname, role, otype, inst, loc, bio, verified in users_data:
            user = User.objects.filter(username=uname).first()
            if not user:
                if role == 'admin':
                    user = User.objects.create_superuser(
                        username=uname, email=email, password=pwd,
                        first_name=fname, last_name=lname, role=role,
                        org_type=otype, institution_name=inst, location=loc, bio=bio,
                        is_verified=verified
                    )
                else:
                    user = User.objects.create_user(
                        username=uname, email=email, password=pwd,
                        first_name=fname, last_name=lname, role=role,
                        org_type=otype, institution_name=inst, location=loc, bio=bio,
                        is_verified=verified
                    )
            else:
                user.role = role
                user.org_type = otype
                user.institution_name = inst
                user.is_verified = verified
                user.save()
            users[uname] = user

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(users)} users (1 admin, 3 organizations, 2 citizens)."))

        # 3. Societal Challenges
        challenges_data = [
            {
                "key": "cold_storage",
                "title": "Affordable Solar-Powered Cold Storage for Perishable Smallholder Harvests",
                "category": categories["agriculture"],
                "creator": users["univ_mit"],
                "location": "Nashik & Pune Rural District, Maharashtra, India",
                "latitude": 19.9975,
                "longitude": 73.7898,
                "severity": "critical",
                "status": "in_progress",
                "organization_name": "MIT Innovation Lab",
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
                "creator": users["ngo_baykeeper"],
                "location": "Austin & San Antonio Municipal Areas, Texas, USA",
                "latitude": 30.2672,
                "longitude": -97.7431,
                "severity": "high",
                "status": "in_progress",
                "organization_name": "Tampa Bay Baykeeper NGO",
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
                "creator": users["ngo_baykeeper"],
                "location": "Tampa Bay Estuary, Florida, USA",
                "latitude": 27.7634,
                "longitude": -82.5437,
                "severity": "high",
                "status": "approved",
                "organization_name": "Tampa Bay Baykeeper NGO",
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
                "key": "flood_warning",
                "title": "Community-Mesh IoT Early Warning Sensor Network for Urban Flash Floods",
                "category": categories["public-safety"],
                "creator": users["student_priya"],
                "location": "Metro Manila River Basin, Philippines",
                "latitude": 14.5995,
                "longitude": 120.9842,
                "severity": "high",
                "status": "approved",
                "organization_name": "Disaster Resilience Youth Circle",
                "description": (
                    "Typhoon season causes rapid inundation in low-lying informal settlements within 20 minutes of torrential rainfall.\n\n"
                    "Centralized weather radar misses micro-basin river surge events, and sirens often activate too late for families to safely evacuate ground-floor belongings.\n\n"
                    "Seeking low-cost ultrasonic water level sensors linked via LoRa wireless mesh that broadcast SMS and audio alerts directly to local council halls."
                ),
                "expected_impact": (
                    "1. Provide a reliable 30-to-45-minute advance flood surge evacuation window.\n"
                    "2. Protect more than 15,000 residents across vulnerable riverbank zones.\n"
                    "3. Total hardware node cost kept below $35 per sensing station."
                ),
            },
            {
                "key": "water_sensor_mesh",
                "title": "Open-Source Water Quality Sensor Mesh for Urban Rivers and Canals",
                "category": categories["technology-and-innovation"],
                "creator": users["student_alex"],
                "location": "Chicago River & Industrial Corridors, Illinois, USA",
                "latitude": 41.8781,
                "longitude": -87.6298,
                "severity": "medium",
                "status": "pending",
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
                    "latitude": cdata.get("latitude"),
                    "longitude": cdata.get("longitude"),
                    "problem_severity": cdata["severity"],
                    "status": cdata["status"],
                    "organization_name": cdata["organization_name"],
                    "description": cdata["description"],
                    "expected_impact": cdata["expected_impact"],
                }
            )
            if not created and (ch.latitude is None or ch.longitude is None):
                ch.latitude = cdata.get("latitude")
                ch.longitude = cdata.get("longitude")
                ch.save(update_fields=['latitude', 'longitude'])
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
                    "Phase 3 (Month 3): Laboratory load testing with 500 kg of fresh produce.\n"
                    "Phase 4 (Month 4): Field deployment at a local agricultural cooperative."
                ),
                "expected_outcome": (
                    "Maintain uninterrupted 4°C - 8°C cooling for 48 hours without grid power.\n"
                    "Extend produce shelf life from 3 days to 21 days.\n"
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
                "pilot_sponsor": users["ind_greenpower"],
                "status": "pilot",
                "progress_percentage": 65,
                "start_date": date.today() - timedelta(days=45),
                "expected_completion_date": date.today() + timedelta(days=75),
                "description": (
                    "Multi-institutional initiative uniting student innovators from MIT, faculty engineering supervisors, and GreenPower Energy Systems.\n\n"
                    "Goal: Fabricate 2 operational 500kg solar cold-rooms and conduct real-world validation."
                ),
                "members": [
                    (users["student_alex"], "Project Lead"),
                    (users["univ_mit"], "Faculty Mentor"),
                    (users["ind_greenpower"], "Industry Advisor"),
                    (users["student_priya"], "Student Researcher"),
                ]
            },
            {
                "key": "waste_sorting_project",
                "title": "AI Robotic Sorter Field Trial - Municipal Facility Deployment",
                "challenge": challenges["waste_sorting"],
                "solution": solutions["waste_sorting_sol"],
                "lead": users["student_priya"],
                "pilot_sponsor": None,
                "status": "active",
                "progress_percentage": 40,
                "start_date": date.today() - timedelta(days=30),
                "expected_completion_date": date.today() + timedelta(days=90),
                "description": (
                    "Partnership between university robotics lab and student AI developers.\n\n"
                    "Deploying a high-speed vision chute at municipal processing center to evaluate real-time plastic segregation."
                ),
                "members": [
                    (users["student_priya"], "Project Lead"),
                    (users["univ_mit"], "Faculty Mentor"),
                    (users["ngo_baykeeper"], "Community Representative"),
                ]
            },
        ]

        projects = {}
        for pdata in projects_data:
            proj, created = Project.objects.get_or_create(
                title=pdata["title"],
                challenge=pdata["challenge"],
                defaults={
                    "solution": pdata["solution"],
                    "lead": pdata["lead"],
                    "pilot_sponsor": pdata["pilot_sponsor"],
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

        self.stdout.write(self.style.SUCCESS(f"Created/Verified {len(projects)} collaborative projects."))

        # 6. Votes & Comments
        for ch in challenges.values():
            for u in users.values():
                Vote.objects.get_or_create(user=u, challenge=ch)

        # Comments
        comments_data = [
            (users["univ_mit"], challenges["cold_storage"], "Our engineering department has tested passive evaporative coolers; pairing with Peltier units is a breakthrough approach!"),
            (users["ind_greenpower"], challenges["cold_storage"], "GreenPower is pleased to sponsor the field pilot and provide high-efficiency solar modules."),
            (users["student_alex"], challenges["cold_storage"], "Thanks for the feedback! We are currently benchmarking phase change salts with 6°C freezing thresholds."),
            (users["ngo_baykeeper"], challenges["waste_sorting"], "We are excited to test automated segregation at the local sorting station!"),
            (users["student_priya"], challenges["waste_sorting"], "Excellent advice; TensorRT benchmark tests confirmed steady 78 FPS with our dataset!"),
        ]

        for u, ch, text in comments_data:
            Comment.objects.get_or_create(
                user=u, challenge=ch, content=text
            )

        # 7. Activity logs
        for u in users.values():
            Activity.objects.get_or_create(
                user=u,
                title="Logged into CivicConnect Platform",
                defaults={"activity_type": "login", "link": "/dashboard/"}
            )

        self.stdout.write(self.style.SUCCESS("Demo database successfully populated with rich data!"))
