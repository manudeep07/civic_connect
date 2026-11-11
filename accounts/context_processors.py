def user_roles_processor(request):
    """
    Context processor to make user role helpers and platform constants easily accessible in all templates.
    Demonstrates Django INT253 CO3 (Templates & Context Processors).
    """
    if request.user.is_authenticated:
        return {
            'current_user_role': request.user.role,
            'is_student_role': request.user.is_student,
            'is_university_role': request.user.is_university,
            'is_industry_role': request.user.is_industry,
            'is_admin_role': request.user.is_admin_user,
        }
    return {
        'current_user_role': None,
        'is_student_role': False,
        'is_university_role': False,
        'is_industry_role': False,
        'is_admin_role': False,
    }

