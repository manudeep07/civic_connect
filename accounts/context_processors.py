def user_roles_processor(request):
    """
    Context processor to make user role helpers and platform constants easily accessible in all templates.
    """
    if request.user.is_authenticated:
        return {
            'current_user_role': request.user.role,
            'is_citizen_role': request.user.is_citizen,
            'is_organization_role': request.user.is_organization,
            'is_student_role': request.user.is_student,
            'is_university_role': request.user.is_university,
            'is_industry_role': request.user.is_industry,
            'is_admin_role': request.user.is_admin_user,
        }
    return {
        'current_user_role': None,
        'is_citizen_role': False,
        'is_organization_role': False,
        'is_student_role': False,
        'is_university_role': False,
        'is_industry_role': False,
        'is_admin_role': False,
    }
