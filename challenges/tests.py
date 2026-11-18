"""
CivicConnect – Full Test Suite
Covers all Phase-2 requirements:
  • Registration cannot create an admin
  • Permission checks on edit / delete
  • Vote toggle
  • Status workflow
  • Moderation bypass attempts
  • Partnership accept / decline flow
Target: ≥ 25 tests, all passing
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from challenges.models import Category, Challenge, Vote, Comment
from solutions.models import Solution
from collaborations.models import Project, ProjectMembership
from partnerships.models import PartnershipRequest

User = get_user_model()

# ---------------------------------------------------------------------------
# Shared base class
# ---------------------------------------------------------------------------

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(
            name="Environment", slug="environment", icon="bi-tree"
        )
        # Student (auto-verified)
        self.student = User.objects.create_user(
            username="student1", email="s@test.com",
            password="testpass99", role="student",
            first_name="Jane", last_name="Doe"
        )
        # Second student
        self.student2 = User.objects.create_user(
            username="student2", email="s2@test.com",
            password="testpass99", role="student"
        )
        # University (not verified by default)
        self.univ = User.objects.create_user(
            username="univ1", email="u@test.com",
            password="testpass99", role="university",
            institution_name="State Uni"
        )
        # Verified university
        self.univ_verified = User.objects.create_user(
            username="univ2", email="u2@test.com",
            password="testpass99", role="university",
            institution_name="MIT East", is_verified=True
        )
        # Industry (not verified)
        self.industry = User.objects.create_user(
            username="ind1", email="i@test.com",
            password="testpass99", role="industry",
            institution_name="Acme Corp"
        )
        # Verified industry
        self.industry_verified = User.objects.create_user(
            username="ind2", email="i2@test.com",
            password="testpass99", role="industry",
            institution_name="BigCo", is_verified=True
        )
        # Admin / superuser
        self.admin = User.objects.create_superuser(
            username="admin1", email="a@test.com",
            password="testpass99", role="admin"
        )

    def _make_challenge(self, creator=None, status="approved", title="Test Challenge"):
        return Challenge.objects.create(
            title=title,
            category=self.category,
            creator=creator or self.student,
            location="Test City",
            problem_severity="high",
            status=status,
            description="Detailed description of the problem.",
            expected_impact="Positive community impact.",
        )

    def _make_solution(self, challenge, creator=None, accepted=False):
        return Solution.objects.create(
            challenge=challenge,
            creator=creator or self.student,
            title="A Good Solution",
            description="Detailed solution description.",
            proposed_implementation="Step by step.",
            expected_outcome="Measured outcomes.",
            required_resources="Resources needed.",
            estimated_duration="3 Months",
            is_accepted=accepted,
        )


# ===========================================================================
# 1. REGISTRATION TESTS
# ===========================================================================

class RegistrationTests(BaseTestCase):
    """Registration form must reject role=admin and enforce min 8-char password."""

    def _register(self, role, password="ValidPass1!", institution="Test Org"):
        data = {
            'username': f'newuser_{role}',
            'email': f'{role}@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': password,
            'confirm_password': password,
            'role': role,
            'location': 'Test City',
        }
        # university and industry require institution_name
        if role in ('university', 'industry'):
            data['institution_name'] = institution
        return self.client.post(reverse('accounts:register'), data)

    def test_registration_rejects_admin_role(self):
        """Submitting role=admin at registration is forbidden."""
        response = self._register('admin')
        self.assertFalse(User.objects.filter(username='newuser_admin').exists(),
                         "Admin role user must NOT be created via public registration.")

    def test_registration_accepts_student_role(self):
        response = self._register('student')
        self.assertTrue(User.objects.filter(username='newuser_student').exists())

    def test_registration_accepts_university_role(self):
        response = self._register('university')
        self.assertTrue(User.objects.filter(username='newuser_university').exists())

    def test_registration_accepts_industry_role(self):
        response = self._register('industry')
        self.assertTrue(User.objects.filter(username='newuser_industry').exists())

    def test_student_auto_verified_on_registration(self):
        """Students and admins must be auto-verified; org roles are not."""
        user = User.objects.create_user(
            username='fresh_student', password='pass12345', role='student'
        )
        self.assertTrue(user.is_verified)

    def test_university_not_auto_verified(self):
        user = User.objects.create_user(
            username='fresh_univ', password='pass12345', role='university'
        )
        self.assertFalse(user.is_verified)

    def test_industry_not_auto_verified(self):
        user = User.objects.create_user(
            username='fresh_ind', password='pass12345', role='industry'
        )
        self.assertFalse(user.is_verified)


# ===========================================================================
# 2. HOME PAGE
# ===========================================================================

class HomePageTests(BaseTestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CivicConnect")
        self.assertContains(response, "Together, We Can")

    def test_home_page_unauthenticated(self):
        """Home page must be accessible without login."""
        self.client.logout()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)


# ===========================================================================
# 3. CHALLENGE EDIT / DELETE PERMISSION TESTS
# ===========================================================================

class ChallengePermissionTests(BaseTestCase):
    def test_creator_can_edit_own_challenge(self):
        challenge = self._make_challenge(creator=self.student, status="pending")
        self.client.login(username="student1", password="testpass99")
        url = reverse('challenges:edit', kwargs={'pk': challenge.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_non_creator_cannot_edit_challenge(self):
        challenge = self._make_challenge(creator=self.student, status="pending")
        self.client.login(username="student2", password="testpass99")
        url = reverse('challenges:edit', kwargs={'pk': challenge.pk})
        response = self.client.get(url)
        # Should be a redirect or 403
        self.assertNotEqual(response.status_code, 200)

    def test_creator_can_delete_own_challenge(self):
        challenge = self._make_challenge(creator=self.student)
        self.client.login(username="student1", password="testpass99")
        url = reverse('challenges:delete', kwargs={'pk': challenge.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Challenge.objects.filter(pk=challenge.pk).exists())

    def test_non_creator_cannot_delete_challenge(self):
        challenge = self._make_challenge(creator=self.student)
        self.client.login(username="student2", password="testpass99")
        url = reverse('challenges:delete', kwargs={'pk': challenge.pk})
        response = self.client.post(url)
        self.assertTrue(Challenge.objects.filter(pk=challenge.pk).exists())

    def test_edit_approved_challenge_reverts_to_pending(self):
        """Editing an approved challenge by non-admin must revert it to pending."""
        challenge = self._make_challenge(creator=self.student, status="approved")
        self.client.login(username="student1", password="testpass99")
        url = reverse('challenges:edit', kwargs={'pk': challenge.pk})
        self.client.post(url, {
            'title': 'Updated Title',
            'category': self.category.pk,
            'location': 'New City',
            'problem_severity': 'low',
            'description': 'Updated description with enough characters.',
            'expected_impact': 'Updated impact statement.',
            'organization_name': '',
        })
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'pending',
                         "Approved challenge edited by creator should revert to pending.")

    def test_admin_edit_approved_challenge_stays_approved(self):
        """Admin editing an approved challenge must NOT revert it to pending."""
        challenge = self._make_challenge(creator=self.student, status="approved")
        self.client.login(username="admin1", password="testpass99")
        url = reverse('challenges:edit', kwargs={'pk': challenge.pk})
        self.client.post(url, {
            'title': 'Admin Updated Title',
            'category': self.category.pk,
            'location': 'Admin City',
            'problem_severity': 'critical',
            'description': 'Admin updated description with enough content.',
            'expected_impact': 'Admin impact statement.',
            'organization_name': '',
        })
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'approved',
                         "Admin editing approved challenge should keep status=approved.")


# ===========================================================================
# 4. VOTING TESTS
# ===========================================================================

class VoteTests(BaseTestCase):
    def test_vote_toggle_adds_vote(self):
        challenge = self._make_challenge(status="approved")
        self.client.login(username="student1", password="testpass99")
        self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(challenge.votes.count(), 1)

    def test_vote_toggle_removes_vote(self):
        challenge = self._make_challenge(status="approved")
        self.client.login(username="student1", password="testpass99")
        # Vote once
        self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        # Toggle off
        self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(challenge.votes.count(), 0)

    def test_cannot_vote_on_pending_challenge(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="student1", password="testpass99")
        self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(challenge.votes.count(), 0,
                         "Votes on pending challenges must be blocked.")

    def test_vote_requires_login(self):
        challenge = self._make_challenge(status="approved")
        response = self.client.post(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertNotEqual(response.status_code, 200)
        self.assertEqual(challenge.votes.count(), 0)

    def test_vote_is_post_only(self):
        challenge = self._make_challenge(status="approved")
        self.client.login(username="student1", password="testpass99")
        response = self.client.get(reverse('challenges:vote_toggle', kwargs={'pk': challenge.pk}))
        self.assertEqual(response.status_code, 405)


# ===========================================================================
# 5. COMMENT TESTS
# ===========================================================================

class CommentTests(BaseTestCase):
    def test_comment_on_approved_challenge(self):
        challenge = self._make_challenge(status="approved")
        self.client.login(username="student1", password="testpass99")
        self.client.post(
            reverse('challenges:comment_add', kwargs={'pk': challenge.pk}),
            {'content': 'Excellent initiative!'}
        )
        self.assertEqual(challenge.comments.count(), 1)

    def test_cannot_comment_on_pending_challenge(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="student1", password="testpass99")
        self.client.post(
            reverse('challenges:comment_add', kwargs={'pk': challenge.pk}),
            {'content': 'Trying to comment.'}
        )
        self.assertEqual(challenge.comments.count(), 0,
                         "Comments on pending challenges must be blocked.")

    def test_delete_own_comment(self):
        challenge = self._make_challenge(status="approved")
        comment = Comment.objects.create(
            challenge=challenge, user=self.student, content="My comment"
        )
        self.client.login(username="student1", password="testpass99")
        self.client.post(reverse('challenges:comment_delete', kwargs={'pk': comment.pk}))
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())

    def test_cannot_delete_others_comment(self):
        challenge = self._make_challenge(status="approved")
        comment = Comment.objects.create(
            challenge=challenge, user=self.student, content="Protected comment"
        )
        self.client.login(username="student2", password="testpass99")
        self.client.post(reverse('challenges:comment_delete', kwargs={'pk': comment.pk}))
        self.assertTrue(Comment.objects.filter(pk=comment.pk).exists())


# ===========================================================================
# 6. ADMIN APPROVE / REJECT
# ===========================================================================

class AdminModerationTests(BaseTestCase):
    def test_admin_approve_requires_post(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="admin1", password="testpass99")
        # GET should return 405
        response = self.client.get(reverse('dashboard:admin_approve', kwargs={'pk': challenge.pk}))
        self.assertEqual(response.status_code, 405)

    def test_admin_approve_via_post(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="admin1", password="testpass99")
        self.client.post(reverse('dashboard:admin_approve', kwargs={'pk': challenge.pk}))
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'approved')

    def test_admin_reject_via_post(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="admin1", password="testpass99")
        self.client.post(reverse('dashboard:admin_reject', kwargs={'pk': challenge.pk}))
        challenge.refresh_from_db()
        self.assertEqual(challenge.status, 'rejected')

    def test_non_admin_cannot_approve(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="student1", password="testpass99")
        self.client.post(reverse('dashboard:admin_approve', kwargs={'pk': challenge.pk}))
        challenge.refresh_from_db()
        self.assertNotEqual(challenge.status, 'approved')


# ===========================================================================
# 7. SOLUTION TESTS
# ===========================================================================

class SolutionTests(BaseTestCase):
    def test_cannot_submit_solution_to_pending_challenge(self):
        challenge = self._make_challenge(status="pending")
        self.client.login(username="student1", password="testpass99")
        response = self.client.post(
            reverse('solutions:create', kwargs={'challenge_id': challenge.pk}),
            {
                'title': 'Blocked Solution',
                'description': 'Some description.',
                'proposed_implementation': 'Some plan.',
                'expected_outcome': 'Some outcome.',
                'required_resources': 'Some resources.',
                'estimated_duration': '1 Month',
            }
        )
        self.assertFalse(Solution.objects.filter(title='Blocked Solution').exists())

    def test_solution_edit_blocked_for_non_creator(self):
        challenge = self._make_challenge(status="approved")
        solution = self._make_solution(challenge, creator=self.student)
        self.client.login(username="student2", password="testpass99")
        url = reverse('solutions:edit', kwargs={'pk': solution.pk})
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, 200)

    def test_accept_toggle_by_challenge_creator(self):
        challenge = self._make_challenge(creator=self.student, status="approved")
        solution = self._make_solution(challenge, creator=self.student2)
        self.client.login(username="student1", password="testpass99")
        self.client.post(reverse('solutions:accept_toggle', kwargs={'pk': solution.pk}))
        solution.refresh_from_db()
        self.assertTrue(solution.is_accepted)

    def test_accept_toggle_blocked_for_unrelated_user(self):
        challenge = self._make_challenge(creator=self.student, status="approved")
        solution = self._make_solution(challenge, creator=self.student2)
        # Login as a third user
        third = User.objects.create_user(
            username='third', password='testpass99', role='student'
        )
        self.client.login(username='third', password='testpass99')
        self.client.post(reverse('solutions:accept_toggle', kwargs={'pk': solution.pk}))
        solution.refresh_from_db()
        self.assertFalse(solution.is_accepted)


# ===========================================================================
# 8. COLLABORATION / PROJECT TESTS
# ===========================================================================

class ProjectTests(BaseTestCase):
    def test_project_requires_accepted_solution(self):
        """Creating a project from an unaccepted solution must be blocked."""
        challenge = self._make_challenge(status="approved")
        solution = self._make_solution(challenge, creator=self.student, accepted=False)
        self.client.login(username="student1", password="testpass99")
        response = self.client.post(
            reverse('collaborations:create_from_solution', kwargs={'solution_id': solution.pk}),
            {
                'title': 'Should Not Create',
                'status': 'planning',
                'progress_percentage': 0,
                'description': 'Attempt to bypass acceptance check.',
            }
        )
        self.assertFalse(Project.objects.filter(title='Should Not Create').exists())

    def test_project_creation_by_non_solution_creator_blocked(self):
        challenge = self._make_challenge(creator=self.student, status="approved")
        solution = self._make_solution(challenge, creator=self.student, accepted=True)
        # student2 is not the solution creator
        self.client.login(username="student2", password="testpass99")
        response = self.client.post(
            reverse('collaborations:create_from_solution', kwargs={'solution_id': solution.pk}),
            {
                'title': 'Unauthorized Project',
                'status': 'planning',
                'progress_percentage': 0,
                'description': 'Should not be created.',
            }
        )
        self.assertFalse(Project.objects.filter(title='Unauthorized Project').exists())

    def test_unverified_university_cannot_lead_project(self):
        challenge = self._make_challenge(creator=self.univ, status="approved")
        solution = self._make_solution(challenge, creator=self.univ, accepted=True)
        self.client.login(username="univ1", password="testpass99")
        response = self.client.post(
            reverse('collaborations:create_from_solution', kwargs={'solution_id': solution.pk}),
            {
                'title': 'Unverified Project',
                'status': 'planning',
                'progress_percentage': 0,
                'description': 'Should be blocked.',
            }
        )
        self.assertFalse(Project.objects.filter(title='Unverified Project').exists(),
                         "Unverified university must not be able to lead a project.")

    def test_quick_join_is_post_only(self):
        challenge = self._make_challenge(status="approved")
        solution = self._make_solution(challenge, creator=self.student, accepted=True)
        project = Project.objects.create(
            title="Open Project",
            challenge=challenge,
            solution=solution,
            lead=self.student,
            status="active",
            description="Open for contributors.",
        )
        self.client.login(username="student2", password="testpass99")
        response = self.client.get(
            reverse('collaborations:join', kwargs={'pk': project.pk})
        )
        self.assertEqual(response.status_code, 405)


# ===========================================================================
# 9. PARTNERSHIP TESTS
# ===========================================================================

class PartnershipTests(BaseTestCase):
    def test_unverified_industry_cannot_send_partnership_request(self):
        self.client.login(username="ind1", password="testpass99")
        response = self.client.post(
            reverse('partnerships:request_create'),
            {
                'target_organization': self.univ_verified.pk,
                'partnership_type': 'technical',
                'message': 'Let us partner!',
            }
        )
        self.assertFalse(
            PartnershipRequest.objects.filter(requesting_organization=self.industry).exists(),
            "Unverified industry must not be able to send partnership requests."
        )

    def test_verified_industry_can_send_partnership_request(self):
        self.client.login(username="ind2", password="testpass99")
        response = self.client.post(
            reverse('partnerships:request_create'),
            {
                'target_organization': self.univ_verified.pk,
                'partnership_type': 'technical',
                'message': 'We want to partner with you!',
            }
        )
        self.assertTrue(
            PartnershipRequest.objects.filter(requesting_organization=self.industry_verified).exists()
        )

    def test_target_can_accept_partnership(self):
        p_req = PartnershipRequest.objects.create(
            requesting_organization=self.industry_verified,
            target_organization=self.univ_verified,
            partnership_type='research',
            message='Research collaboration.',
            status='pending',
        )
        self.client.login(username="univ2", password="testpass99")
        self.client.post(
            reverse('partnerships:respond', kwargs={'pk': p_req.pk}),
            {'status': 'accepted', 'response_note': 'Glad to partner!'}
        )
        p_req.refresh_from_db()
        self.assertEqual(p_req.status, 'accepted')

    def test_target_can_decline_partnership(self):
        p_req = PartnershipRequest.objects.create(
            requesting_organization=self.industry_verified,
            target_organization=self.univ_verified,
            partnership_type='research',
            message='Would you join us?',
            status='pending',
        )
        self.client.login(username="univ2", password="testpass99")
        self.client.post(
            reverse('partnerships:respond', kwargs={'pk': p_req.pk}),
            {'status': 'rejected', 'response_note': 'Not at this time.'}
        )
        p_req.refresh_from_db()
        # Model uses 'rejected' to mean Declined
        self.assertEqual(p_req.status, 'rejected')

    def test_non_target_cannot_respond_to_partnership(self):
        p_req = PartnershipRequest.objects.create(
            requesting_organization=self.industry_verified,
            target_organization=self.univ_verified,
            partnership_type='research',
            message='Private request.',
            status='pending',
        )
        # student2 is not the target — should get 404 or redirect
        self.client.login(username="student2", password="testpass99")
        response = self.client.post(
            reverse('partnerships:respond', kwargs={'pk': p_req.pk}),
            {'status': 'accepted', 'response_note': 'Hacked!'}
        )
        p_req.refresh_from_db()
        self.assertEqual(p_req.status, 'pending',
                         "Non-target must not be able to respond to a partnership request.")

    def test_logout_requires_post(self):
        self.client.login(username="student1", password="testpass99")
        response = self.client.get(reverse('accounts:logout'))
        # GET on logout must return 405
        self.assertEqual(response.status_code, 405)

    def test_dashboard_loads_for_all_roles(self):
        for username, text in [
            ("student1", "Citizen"),
            ("univ1", "Academic"),
            ("ind1", "Corporate"),
            ("admin1", "Administration"),
        ]:
            self.client.login(username=username, password="testpass99")
            response = self.client.get(reverse('dashboard:index'))
            self.assertEqual(response.status_code, 200)



# ===========================================================================
# 10. PHASE 3 FEATURE TESTS
# ===========================================================================

class AnalyticsTests(BaseTestCase):
    def test_unauthenticated_user_cannot_access_analytics(self):
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 302)

    def test_student_cannot_access_analytics(self):
        self.client.login(username="student1", password="testpass99")
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 302)

    def test_unverified_industry_cannot_access_analytics(self):
        self.client.login(username="ind1", password="testpass99")
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 302)

    def test_verified_industry_can_access_analytics(self):
        self.client.login(username="ind2", password="testpass99")
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Analytics")

    def test_admin_can_access_analytics(self):
        self.client.login(username="admin1", password="testpass99")
        response = self.client.get(reverse('dashboard:analytics'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Analytics")


class PilotSponsorTests(BaseTestCase):
    def test_verified_industry_can_sponsor_pilot(self):
        challenge = self._make_challenge(status="approved")
        solution = self._make_solution(challenge, creator=self.student, accepted=True)
        project = Project.objects.create(
            title="Clean Rivers Project",
            challenge=challenge,
            solution=solution,
            lead=self.student,
            status="active",
            description="Active project ready for pilot."
        )
        self.client.login(username="ind2", password="testpass99")
        url = reverse('collaborations:sponsor_pilot', kwargs={'pk': project.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        project.refresh_from_db()
        self.assertEqual(project.status, 'pilot')
        self.assertEqual(project.pilot_sponsor, self.industry_verified)

    def test_unverified_industry_cannot_sponsor_pilot(self):
        challenge = self._make_challenge(status="approved")
        solution = self._make_solution(challenge, creator=self.student, accepted=True)
        project = Project.objects.create(
            title="Clean Rivers Project 2",
            challenge=challenge,
            solution=solution,
            lead=self.student,
            status="active",
            description="Active project."
        )
        self.client.login(username="ind1", password="testpass99")
        url = reverse('collaborations:sponsor_pilot', kwargs={'pk': project.pk})
        response = self.client.post(url)
        project.refresh_from_db()
        self.assertNotEqual(project.status, 'pilot')
        self.assertIsNone(project.pilot_sponsor)


class LeaderboardTests(BaseTestCase):
    def test_leaderboard_page_loads(self):
        self.client.login(username="student1", password="testpass99")
        response = self.client.get(reverse('dashboard:leaderboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Contributor Leaderboard")

    def test_points_awarded_on_challenge_creation(self):
        from accounts.models import UserScore
        self.client.login(username="student1", password="testpass99")
        post_data = {
            'title': 'Leaderboard Challenge',
            'category': self.category.id,
            'location': 'New York',
            'problem_severity': 'medium',
            'description': 'Valid challenge description here.',
            'expected_impact': 'Impact statement.',
        }
        self.client.post(reverse('challenges:create'), post_data)
        self.assertTrue(
            UserScore.objects.filter(user=self.student, event_type='challenge_created').exists()
        )


class MapViewTests(BaseTestCase):
    def test_map_page_loads(self):
        response = self.client.get(reverse('challenges:map'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Challenge Map")

    def test_map_view_output_with_and_without_coordinates(self):
        ch_with_coords = Challenge.objects.create(
            title="Mapped Challenge",
            category=self.category,
            creator=self.student,
            location="Miami, FL",
            latitude=25.7617,
            longitude=-80.1918,
            status="approved",
            problem_severity="medium",
            description="Challenge with coords.",
            expected_impact="Impact",
        )
        ch_without_coords = Challenge.objects.create(
            title="Unmapped Challenge",
            category=self.category,
            creator=self.student,
            location="Nowhere",
            latitude=None,
            longitude=None,
            status="approved",
            problem_severity="low",
            description="Challenge without coords.",
            expected_impact="Impact",
        )
        response = self.client.get(reverse('challenges:map'))
        self.assertEqual(response.status_code, 200)
        markers = response.context['markers']
        marker_ids = [m['id'] for m in markers]
        self.assertIn(ch_with_coords.pk, marker_ids)
        self.assertNotIn(ch_without_coords.pk, marker_ids)
        self.assertContains(response, 'id="markers-data"')

    def test_map_xss_escaping(self):
        xss_title = '</script><img src=x onerror=alert(1)>'
        xss_location = '<script>alert("xss")</script>'
        ch = Challenge.objects.create(
            title=xss_title,
            category=self.category,
            creator=self.student,
            location=xss_location,
            latitude=12.3456,
            longitude=65.4321,
            status="approved",
            problem_severity="high",
            description="XSS test challenge.",
            expected_impact="Impact",
        )
        response = self.client.get(reverse('challenges:map'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        # Django's json_script must escape < to \u003C so malicious tags cannot break out
        self.assertNotIn('</script><img', content)
        self.assertIn(r'\u003C/script\u003E\u003Cimg', content)


class CoordinateValidationTests(BaseTestCase):
    def test_valid_coordinates(self):
        from challenges.forms import ChallengeForm
        data = {
            'title': 'Solar panels in rural area',
            'category': self.category.pk,
            'location': 'Austin, TX',
            'latitude': 30.2672,
            'longitude': -97.7431,
            'problem_severity': 'high',
            'description': 'Valid description with enough characters.',
            'expected_impact': 'Positive impact statement.',
        }
        form = ChallengeForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_both_coordinates_empty_is_valid(self):
        from challenges.forms import ChallengeForm
        data = {
            'title': 'Solar panels without coordinates',
            'category': self.category.pk,
            'location': 'Austin, TX',
            'latitude': '',
            'longitude': '',
            'problem_severity': 'high',
            'description': 'Valid description with enough characters.',
            'expected_impact': 'Positive impact statement.',
        }
        form = ChallengeForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)

    def test_latitude_without_longitude_is_invalid(self):
        from challenges.forms import ChallengeForm
        data = {
            'title': 'Partial coordinates',
            'category': self.category.pk,
            'location': 'Austin, TX',
            'latitude': 30.2672,
            'longitude': '',
            'problem_severity': 'high',
            'description': 'Valid description.',
            'expected_impact': 'Positive impact.',
        }
        form = ChallengeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Both latitude and longitude must be provided together", str(form.non_field_errors()))

    def test_longitude_without_latitude_is_invalid(self):
        from challenges.forms import ChallengeForm
        data = {
            'title': 'Partial coordinates',
            'category': self.category.pk,
            'location': 'Austin, TX',
            'latitude': '',
            'longitude': -97.7431,
            'problem_severity': 'high',
            'description': 'Valid description.',
            'expected_impact': 'Positive impact.',
        }
        form = ChallengeForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn("Both latitude and longitude must be provided together", str(form.non_field_errors()))

    def test_latitude_out_of_bounds_is_invalid(self):
        from challenges.forms import ChallengeForm
        for invalid_lat in [90.1, -95.0, 150.0]:
            data = {
                'title': 'Out of bounds lat',
                'category': self.category.pk,
                'location': 'North Pole',
                'latitude': invalid_lat,
                'longitude': 0.0,
                'problem_severity': 'low',
                'description': 'Valid description.',
                'expected_impact': 'Positive impact.',
            }
            form = ChallengeForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('latitude', form.errors)

    def test_longitude_out_of_bounds_is_invalid(self):
        from challenges.forms import ChallengeForm
        for invalid_lng in [180.5, -185.0, 250.0]:
            data = {
                'title': 'Out of bounds lng',
                'category': self.category.pk,
                'location': 'Fiji',
                'latitude': 10.0,
                'longitude': invalid_lng,
                'problem_severity': 'low',
                'description': 'Valid description.',
                'expected_impact': 'Positive impact.',
            }
            form = ChallengeForm(data=data)
            self.assertFalse(form.is_valid())
            self.assertIn('longitude', form.errors)


# ===========================================================================
# 11. PHASE 1 SMOKE AND REGRESSION TESTS
# ===========================================================================

class SmokeAndRegressionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        import io
        from django.core.management import call_command
        out = io.StringIO()
        call_command('populate_db', stdout=out)

    def setUp(self):
        self.client = Client()

    def test_smoke_all_pages_all_roles(self):
        """
        Smoke test using seeded data: requests EVERY GET page as anonymous,
        student, university, industry and admin users, and asserts there is no 500 error.
        """
        challenge = Challenge.objects.filter(status__in=['approved', 'in_progress']).first()
        solution = Solution.objects.first()
        project = Project.objects.first()
        sample_user = User.objects.first()

        urls = [
            reverse('home'),
            reverse('about'),
            reverse('accounts:login'),
            reverse('accounts:register'),
            reverse('challenges:list'),
            reverse('challenges:map'),
            reverse('challenges:detail', kwargs={'pk': challenge.pk}),
            reverse('solutions:detail', kwargs={'pk': solution.pk}),
            reverse('collaborations:list'),
            reverse('collaborations:detail', kwargs={'pk': project.pk}),
            reverse('partnerships:directory'),
            reverse('dashboard:leaderboard'),
            reverse('dashboard:analytics'),
            reverse('accounts:profile'),
            reverse('accounts:user_detail', kwargs={'username': sample_user.username}),
        ]

        roles_users = [
            (None, None),  # Anonymous
            ('student_alex', 'alex123'),
            ('univ_mit', 'mit123'),
            ('ind_greenpower', 'green123'),
            ('admin', 'admin123'),
        ]

        for username, password in roles_users:
            if username:
                logged_in = self.client.login(username=username, password=password)
                self.assertTrue(logged_in, f"Failed to login user {username}")
            else:
                self.client.logout()

            for url in urls:
                with self.subTest(user=username or 'anonymous', url=url):
                    response = self.client.get(url)
                    self.assertNotEqual(
                        response.status_code, 500,
                        f"URL '{url}' returned 500 for user '{username or 'anonymous'}'"
                    )

    def test_challenge_detail_regression_with_accepted_solution(self):
        """
        Regression test for challenge detail page when a solution is accepted.
        Verifies template renders properly with accepted_solution in context and no 500.
        """
        challenge = Challenge.objects.filter(solutions__is_accepted=True, status__in=['approved', 'in_progress']).first()
        self.assertIsNotNone(challenge, "Seeded data should have a challenge with an accepted solution")

        # Anonymous request
        self.client.logout()
        res_anon = self.client.get(reverse('challenges:detail', kwargs={'pk': challenge.pk}))
        self.assertEqual(res_anon.status_code, 200)
        self.assertIsNotNone(res_anon.context.get('accepted_solution'))

        # Authenticated student request
        self.client.login(username='student_alex', password='alex123')
        res_auth = self.client.get(reverse('challenges:detail', kwargs={'pk': challenge.pk}))
        self.assertEqual(res_auth.status_code, 200)
        self.assertContains(res_auth, "Launch Project for Solution")

    def test_challenge_detail_regression_without_accepted_solution(self):
        """
        Regression test for challenge detail page when NO solution is accepted.
        Verifies template renders properly without errors and does not show Launch Project button.
        """
        category = Category.objects.first()
        user = User.objects.filter(role='student').first()
        ch_no_accepted = Challenge.objects.create(
            title="Challenge without accepted solutions",
            category=category,
            creator=user,
            location="Testville",
            problem_severity="low",
            status="approved",
            description="A problem waiting for solutions.",
            expected_impact="High impact",
        )
        # Create an unaccepted solution
        Solution.objects.create(
            challenge=ch_no_accepted,
            creator=user,
            title="Pending solution",
            description="Not yet accepted",
            proposed_implementation="Steps",
            expected_outcome="Outcome",
            required_resources="Resources",
            estimated_duration="2 weeks",
            is_accepted=False
        )

        self.client.login(username='student_alex', password='alex123')
        res = self.client.get(reverse('challenges:detail', kwargs={'pk': ch_no_accepted.pk}))
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.context.get('accepted_solution'))
        self.assertNotContains(res, "Launch Project for Solution")

    def test_challenge_list_not_on_map_badge(self):
        """
        Verifies that challenges with empty latitude/longitude show 'Not on map' badge on challenge cards.
        """
        category = Category.objects.first()
        user = User.objects.filter(role='student').first()
        ch_unmapped = Challenge.objects.create(
            title="Unmapped Challenge Card",
            category=category,
            creator=user,
            location="Remote Village",
            problem_severity="medium",
            status="approved",
            description="Challenge without coordinates.",
            expected_impact="High impact",
            latitude=None,
            longitude=None,
        )

        res = self.client.get(reverse('challenges:list'))
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, "Not on map")
        self.assertContains(res, "Unmapped Challenge Card")
