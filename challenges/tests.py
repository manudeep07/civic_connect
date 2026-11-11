from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from challenges.models import Category, Challenge, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from partnerships.models import PartnershipRequest

User = get_user_model()


class CivicConnectFullFlowTests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Category
        self.category = Category.objects.create(
            name="Environment",
            slug="environment",
            icon="bi-tree"
        )

        # Create Users
        self.student = User.objects.create_user(
            username="student_tester",
            email="student@test.com",
            password="password123",
            role="student",
            first_name="Jane",
            last_name="Student"
        )

        self.university = User.objects.create_user(
            username="univ_tester",
            email="univ@test.com",
            password="password123",
            role="university",
            institution_name="Global Tech University",
            first_name="Prof",
            last_name="Tech"
        )

        self.industry = User.objects.create_user(
            username="industry_tester",
            email="industry@test.com",
            password="password123",
            role="industry",
            institution_name="Apex Energy Corp"
        )

        self.admin_user = User.objects.create_superuser(
            username="admin_tester",
            email="admin@test.com",
            password="password123",
            role="admin"
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Together, We Can")
        self.assertContains(response, "Solve Real-World")
        self.assertContains(response, "CivicConnect")

    def test_challenge_creation_and_approval_workflow(self):
        # 1. Student submits challenge -> pending status
        self.client.login(username="student_tester", password="password123")
        post_data = {
            'title': 'Test Estuary Plastic Cleanup',
            'category': self.category.id,
            'location': 'Test Estuary, Florida',
            'problem_severity': 'high',
            'description': 'Heavy synthetic runoff threatening mangroves and local fauna.',
            'expected_impact': 'Eliminate 70% of floating particulate plastics.',
            'organization_name': 'Test Conservation Forum',
        }
        response = self.client.post(reverse('challenges:create'), post_data)
        self.assertEqual(response.status_code, 302)

        challenge = Challenge.objects.get(title='Test Estuary Plastic Cleanup')
        self.assertEqual(challenge.status, 'pending')

        # Public list shouldn't show pending challenge to unauthenticated users
        self.client.logout()
        res_list = self.client.get(reverse('challenges:list'))
        self.assertNotContains(res_list, 'Test Estuary Plastic Cleanup')

        # Admin approves challenge via 1-click approve view
        self.client.login(username="admin_tester", password="password123")
        res_approve = self.client.get(reverse('dashboard:admin_approve', kwargs={'pk': challenge.pk}))
        self.assertEqual(res_approve.status_code, 302)

        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'approved')

        # Now public list shows approved challenge
        self.client.logout()
        res_list_after = self.client.get(reverse('challenges:list'))
        self.assertContains(res_list_after, 'Test Estuary Plastic Cleanup')

    def test_upvoting_and_comments(self):
        challenge = Challenge.objects.create(
            title="Clean Drinking Water in Tribal Hamlets",
            category=self.category,
            creator=self.student,
            location="Bastar District",
            problem_severity="critical",
            status="approved",
            description="Remote hamlets lack potable groundwater filtration systems.",
            expected_impact="Provide 2,000 residents safe water."
        )

        self.client.login(username="student_tester", password="password123")

        # 1. Upvote
        res_vote = self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(res_vote.status_code, 302)
        self.assertEqual(challenge.votes_count, 1)

        # 2. Toggle Upvote off
        res_unvote = self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(res_unvote.status_code, 302)
        self.assertEqual(challenge.votes_count, 0)

        # 3. Add Comment
        res_comment = self.client.post(reverse('challenges:comment_add', kwargs={'pk': challenge.pk}), {
            'content': 'We could deploy solar-powered UV purification kits here.'
        })
        self.assertEqual(res_comment.status_code, 302)
        self.assertEqual(challenge.comments.count(), 1)
        comment = challenge.comments.first()
        self.assertEqual(comment.user, self.student)

        # 4. Delete own comment
        res_del_comment = self.client.post(reverse('challenges:comment_delete', kwargs={'pk': comment.pk}))
        self.assertEqual(res_del_comment.status_code, 302)
        self.assertEqual(challenge.comments.count(), 0)

    def test_solution_submission_acceptance_and_project_launch(self):
        challenge = Challenge.objects.create(
            title="Solar Irrigation for Drought Prone Farms",
            category=self.category,
            creator=self.university,
            location="Vidarbha, Maharashtra",
            problem_severity="critical",
            status="approved",
            description="Groundwater pumping is severely limited by erratic grid power.",
            expected_impact="Ensure continuous drip irrigation for 50 acres."
        )

        # Student submits solution
        self.client.login(username="student_tester", password="password123")
        sol_data = {
            'title': 'Smart IoT DC Solar Drip Pump System',
            'estimated_duration': '3 Months',
            'description': 'Direct drive DC submersible pump with capacitive IoT moisture sensors.',
            'proposed_implementation': 'Fabricate pump controller and field test on 5 acre plot.',
            'expected_outcome': 'Reduce water consumption by 40% and zero fuel reliance.',
            'required_resources': 'Solar panels, DC pump, ESP32 microcontroller.',
        }
        res_sol = self.client.post(reverse('solutions:create', kwargs={'challenge_id': challenge.pk}), sol_data)
        self.assertEqual(res_sol.status_code, 302)

        solution = Solution.objects.get(title='Smart IoT DC Solar Drip Pump System')
        self.assertEqual(solution.is_accepted, False)

        # University (Challenge Creator) accepts solution
        self.client.login(username="univ_tester", password="password123")
        res_accept = self.client.post(reverse('solutions:accept_toggle', kwargs={'pk': solution.pk}))
        self.assertEqual(res_accept.status_code, 302)

        solution.refresh_from_db()
        self.assertEqual(solution.is_accepted, True)

        # Launch Project from Accepted Solution
        self.client.login(username="student_tester", password="password123")
        proj_data = {
            'title': 'Solar Drip Pump Deployment Initiative',
            'status': 'active',
            'progress_percentage': 15,
            'description': 'Collaborative deployment across Vidarbha farming communities.',
        }
        res_proj = self.client.post(reverse('collaborations:create_from_solution', kwargs={'solution_id': solution.pk}), proj_data)
        self.assertEqual(res_proj.status_code, 302)

        project = Project.objects.get(title='Solar Drip Pump Deployment Initiative')
        self.assertEqual(project.lead, self.student)
        self.assertTrue(project.is_member(self.student))

        # Add University Mentor to Project Team
        self.client.post(reverse('collaborations:member_add', kwargs={'pk': project.pk}), {
            'user': self.university.id,
            'role': 'Faculty Mentor',
        })
        self.assertTrue(project.is_member(self.university))

    def test_partnership_request_workflow(self):
        self.client.login(username="industry_tester", password="password123")

        # Industry sends partnership request to University
        req_data = {
            'target_organization': self.university.id,
            'partnership_type': 'technical',
            'message': 'We would like to co-sponsor university research into renewable energy microgrids.',
        }
        res_req = self.client.post(reverse('partnerships:request_create'), req_data)
        self.assertEqual(res_req.status_code, 302)

        p_req = PartnershipRequest.objects.get(requesting_organization=self.industry)
        self.assertEqual(p_req.status, 'pending')

        # University logs in and accepts the request
        self.client.login(username="univ_tester", password="password123")
        res_respond = self.client.post(reverse('partnerships:respond', kwargs={'pk': p_req.pk}), {
            'status': 'accepted',
            'response_note': 'We are pleased to partner with Apex Energy Corp.',
        })
        self.assertEqual(res_respond.status_code, 302)

        p_req.refresh_from_db()
        self.assertEqual(p_req.status, 'accepted')

    def test_dashboards_render_for_all_roles(self):
        # 1. Student Dashboard
        self.client.login(username="student_tester", password="password123")
        res_student = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res_student.status_code, 200)
        self.assertContains(res_student, "Citizen & Student Innovator Dashboard")

        # 2. University Dashboard
        self.client.login(username="univ_tester", password="password123")
        res_univ = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res_univ.status_code, 200)
        self.assertContains(res_univ, "Academic Partner Portal")

        # 3. Industry Dashboard
        self.client.login(username="industry_tester", password="password123")
        res_ind = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res_ind.status_code, 200)
        self.assertContains(res_ind, "Corporate & CSR Partner Portal")

        # 4. Admin Dashboard
        self.client.login(username="admin_tester", password="password123")
        res_admin = self.client.get(reverse('dashboard:index'))
        self.assertEqual(res_admin.status_code, 200)
        self.assertContains(res_admin, "Superuser / Staff Administration")
