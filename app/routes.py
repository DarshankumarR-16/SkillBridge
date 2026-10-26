from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    current_app,
)

from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import (
    User,
    Profile,
    Skill,
    UserSkill,
    LearningResource,
    Project,
    ProjectSkill,
    Recommendation,
    Team,
    TeamMember,
    TeamJoinRequest,
)


auth = Blueprint("auth", __name__)


@auth.route("/register", methods=["GET", "POST"])
def register():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not name or not email or not password or not confirm_password:
            flash("Please fill in every field.", "danger")
        elif len(name) > 100:
            flash("Name must be 100 characters or fewer.", "danger")
        elif len(email) > 120 or "@" not in email:
            flash("Please enter a valid email address.", "danger")
        elif len(password) < 8:
            flash("Password must contain at least 8 characters.", "danger")
        elif password != confirm_password:
            flash("Passwords do not match.", "danger")
        elif User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "danger")
        else:
            user = User(
                name=name,
                email=email,
                password_hash=generate_password_hash(password),
                role="student",
            )
            db.session.add(user)

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                flash("An account with this email already exists.", "danger")
            else:
                session.clear()
                session["user_id"] = user.id
                session["user_role"] = user.role
                session["user_name"] = user.name
                flash("Registration successful. Welcome to SkillBridge!", "success")
                return redirect(url_for("index"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.is_active and check_password_hash(
            user.password_hash, password
        ):
            session.clear()
            session["user_id"] = user.id
            session["user_role"] = user.role
            session["user_name"] = user.name
            flash("Login successful. Welcome back!", "success")
            return redirect(url_for("index"))

        flash("Invalid email or password, or the account is inactive.", "danger")

    return render_template("login.html")


@auth.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))

    
@auth.route("/profile")
def profile():
    if not session.get("user_id"):
        flash("Please log in to view your profile.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    profile_data = Profile.query.filter_by(user_id=user.id).first()

    return render_template(
        "profile.html",
        user=user,
        profile=profile_data,
    )


@auth.route("/profile/edit", methods=["GET", "POST"])
def edit_profile():
    if not session.get("user_id"):
        flash("Please log in to edit your profile.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    profile_data = Profile.query.filter_by(user_id=user.id).first()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        bio = request.form.get("bio", "").strip()
        education = request.form.get("education", "").strip()
        interests = request.form.get("interests", "").strip()

        if profile_data is None:
            profile_data = Profile(user_id=user.id)
            db.session.add(profile_data)

        if not name:
            flash("Name is required.", "danger")
        elif len(name) > 100:
            flash("Name must be 100 characters or fewer.", "danger")
        elif len(education) > 150:
            flash("Education must be 150 characters or fewer.", "danger")
        else:
            user.name = name
            profile_data.bio = bio or None
            profile_data.education = education or None
            profile_data.interests = interests or None

            db.session.commit()
            session["user_name"] = user.name

            flash("Your profile has been updated!", "success")
            return redirect(url_for("auth.profile"))

    return render_template(
        "edit_profile.html",
        user=user,
        profile=profile_data,
    )


@auth.route("/skills", methods=["GET"])
def skills():
    if not session.get("user_id"):
        flash("Please log in to view your skills.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    user_skills = (
        db.session.query(UserSkill, Skill)
        .join(Skill, UserSkill.skill_id == Skill.id)
        .filter(UserSkill.user_id == user.id)
        .order_by(Skill.name.asc())
        .all()
    )
    available_skills = (
        Skill.query
        .filter(
            ~Skill.id.in_(
                db.session.query(UserSkill.skill_id)
                .filter(UserSkill.user_id == user.id)
            )
        )
        .order_by(Skill.name.asc())
        .all()
    )

    return render_template(
        "skills.html",
        user_skills=user_skills,
        available_skills=available_skills,
    )


@auth.route("/skills/add", methods=["POST"])
def add_skill():
    if not session.get("user_id"):
        flash("Please log in to add a skill.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    skill_id = request.form.get("skill_id", type=int)
    proficiency_level = request.form.get("proficiency_level", type=int)

    skill = db.session.get(Skill, skill_id) if skill_id else None

    if skill is None:
        flash("Please select a valid skill.", "danger")
    elif proficiency_level not in (1, 2, 3, 4, 5):
        flash("Please select a valid proficiency level.", "danger")
    elif UserSkill.query.filter_by(
        user_id=user.id,
        skill_id=skill.id,
    ).first():
        flash("You have already added this skill.", "warning")
    else:
        student_skill = UserSkill(
            user_id=user.id,
            skill_id=skill.id,
            proficiency_level=proficiency_level,
        )

        db.session.add(student_skill)
        db.session.commit()

        flash(f"{skill.name} added successfully!", "success")

    return redirect(url_for("auth.skills"))


@auth.route("/skills/<int:skill_id>/edit", methods=["GET", "POST"])
def edit_skill(skill_id):
    if not session.get("user_id"):
        flash("Please log in to edit your skills.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    user_skill = UserSkill.query.filter_by(
        user_id=user.id,
        skill_id=skill_id,
    ).first()

    if user_skill is None:
        flash("Skill not found in your profile.", "danger")
        return redirect(url_for("auth.skills"))

    skill = db.session.get(Skill, skill_id)

    if request.method == "POST":
        proficiency_level = request.form.get(
            "proficiency_level", type=int
        )

        if proficiency_level not in (1, 2, 3, 4, 5):
            flash("Please select a valid proficiency level.", "danger")
        else:
            user_skill.proficiency_level = proficiency_level
            db.session.commit()
            flash(f"{skill.name} proficiency updated successfully!", "success")
            return redirect(url_for("auth.skills"))

    return render_template(
        "edit_skill.html",
        user_skill=user_skill,
        skill=skill,
    )

@auth.route("/skills/<int:skill_id>/delete", methods=["POST"])
def delete_skill(skill_id):
    if not session.get("user_id"):
        flash("Please log in to remove a skill.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    user_skill = UserSkill.query.filter_by(
        user_id=user.id,
        skill_id=skill_id,
    ).first()

    if user_skill is None:
        flash("Skill not found in your profile.", "danger")
    else:
        db.session.delete(user_skill)
        db.session.commit()
        flash("Skill removed successfully.", "success")

    return redirect(url_for("auth.skills"))

@auth.route("/learning-resources", methods=["GET"])
def learning_resources():
    if not session.get("user_id"):
        flash("Please log in to view learning resources.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    selected_skill = request.args.get("skill_id", type=int)
    selected_difficulty = request.args.get("difficulty", "").strip().lower()

    query = (
        db.session.query(LearningResource, Skill)
        .outerjoin(Skill, LearningResource.skill_id == Skill.id)
        .filter(LearningResource.is_active.is_(True))
    )

    if selected_skill:
        query = query.filter(LearningResource.skill_id == selected_skill)

    if selected_difficulty in ("beginner", "intermediate", "advanced"):
        query = query.filter(
            LearningResource.difficulty == selected_difficulty
        )
    else:
        selected_difficulty = ""

    resources = query.order_by(LearningResource.title.asc()).all()
    skills = Skill.query.order_by(Skill.name.asc()).all()

    return render_template(
        "learning_resources.html",
        resources=resources,
        skills=skills,
        selected_skill=selected_skill,
        selected_difficulty=selected_difficulty,
    )


@auth.route("/recommendations", methods=["GET"])
def project_recommendations():
    if not session.get("user_id"):
        flash("Please log in to view project recommendations.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    user_skills = {
        item.skill_id: item.proficiency_level
        for item in UserSkill.query.filter_by(user_id=user.id).all()
    }

    projects = Project.query.filter_by(is_active=True).all()
    recommendations = []

    for project in projects:
        required_skills = ProjectSkill.query.filter_by(
            project_id=project.id
        ).all()

        matched_skills = []
        missing_skills = []
        total_score = 0
        valid_requirements = 0

        for required in required_skills:
            skill = db.session.get(Skill, required.skill_id)

            if skill is None:
                continue

            valid_requirements += 1
            student_level = user_skills.get(required.skill_id, 0)
            required_level = required.required_level or 1

            if student_level >= required_level:
                total_score += 1
                matched_skills.append(skill.name)
            else:
                total_score += min(student_level / required_level, 1)
                missing_skills.append(skill.name)

        if valid_requirements == 0:
            continue

        match_score = round(
            (total_score / valid_requirements) * 100
        )

        if matched_skills:
            explanation = (
                "Your matching skills: "
                + ", ".join(matched_skills)
                + "."
            )
        else:
            explanation = "Build the required skills to get started."

        if missing_skills:
            explanation += (
                " Skills to improve: "
                + ", ".join(missing_skills)
                + "."
            )

        saved_recommendation = Recommendation.query.filter_by(
            user_id=user.id,
            project_id=project.id,
        ).first()

        if saved_recommendation is None:
            saved_recommendation = Recommendation(
                user_id=user.id,
                project_id=project.id,
                match_score=match_score,
                explanation=explanation,
                status="active",
            )
            db.session.add(saved_recommendation)
        else:
            saved_recommendation.match_score = match_score
            saved_recommendation.explanation = explanation
            saved_recommendation.status = "active"

        recommendations.append({
            "project": project,
            "match_score": match_score,
            "explanation": explanation,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
        })

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    recommendations.sort(
        key=lambda item: item["match_score"],
        reverse=True,
    )

    return render_template(
        "recommendations.html",
        recommendations=recommendations,
    )

@auth.route("/teams", methods=["GET"])
def teams():
    if not session.get("user_id"):
        flash("Please log in to view teams.", "warning")
        return redirect(url_for("auth.login"))

    user = db.session.get(User, session["user_id"])

    if user is None or not user.is_active:
        session.clear()
        flash("Please log in again.", "warning")
        return redirect(url_for("auth.login"))

    all_teams = (
        db.session.query(Team, Project)
        .outerjoin(Project, Team.project_id == Project.id)
        .filter(Team.status.in_(["open", "active"]))
        .order_by(Team.created_at.desc())
        .all()
    )

    team_data = []

    for team, project in all_teams:
        member_count = TeamMember.query.filter_by(
            team_id=team.id
        ).count()

        team_data.append({
            "team": team,
            "project": project,
            "member_count": member_count,
            "is_full": member_count >= team.max_members,
        })

    return render_template(
        "teams.html",
        teams=team_data,
        current_user_id=user.id,
    )
    
# --------------------------------------------------
# TEAM COLLABORATION ROUTES
# Add these routes below the existing teams() route.
# --------------------------------------------------


def _get_active_user():
    """Return the logged-in active user, or None."""
    user_id = session.get("user_id")

    if not user_id:
        return None

    user = db.session.get(User, user_id)

    if user is None or not user.is_active:
        session.clear()
        return None

    return user


@auth.route("/teams/create", methods=["GET", "POST"])
def create_team():
    user = _get_active_user()

    if user is None:
        flash("Please log in to create a team.", "warning")
        return redirect(url_for("auth.login"))

    available_projects = Project.query.filter_by(is_active=True).order_by(
        Project.title.asc()
    ).all()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        project_id = request.form.get("project_id", type=int)
        max_members = request.form.get("max_members", type=int)

        project = db.session.get(Project, project_id) if project_id else None

        if not name:
            flash("Team name is required.", "danger")
        elif len(name) > 120:
            flash("Team name must be 120 characters or fewer.", "danger")
        elif max_members is None or not 2 <= max_members <= 50:
            flash("Team size must be between 2 and 50 members.", "danger")
        elif project_id and (
            project is None or not project.is_active
        ):
            flash("Please select a valid active project.", "danger")
        else:
            team = Team(
                name=name,
                description=description or None,
                project_id=project.id if project else None,
                created_by=user.id,
                max_members=max_members,
                status="open",
            )

            try:
                db.session.add(team)
                db.session.flush()

                leader = TeamMember(
                    team_id=team.id,
                    user_id=user.id,
                    role="leader",
                )
                db.session.add(leader)
                db.session.commit()

            except IntegrityError:
                db.session.rollback()
                flash("The team could not be created. Please try again.", "danger")
            else:
                flash("Team created successfully!", "success")
                return redirect(url_for("auth.my_teams"))

    return render_template(
        "create_team.html",
        projects=available_projects,
    )


@auth.route("/teams/<int:team_id>/join", methods=["POST"])
def join_team(team_id):
    user = _get_active_user()

    if user is None:
        flash("Please log in to request to join a team.", "warning")
        return redirect(url_for("auth.login"))

    team = db.session.get(Team, team_id)

    if team is None or team.status not in ("open", "active"):
        flash("This team is unavailable.", "danger")
        return redirect(url_for("auth.teams"))

    if team.created_by == user.id:
        flash("You are already the creator of this team.", "info")
        return redirect(url_for("auth.teams"))

    existing_member = TeamMember.query.filter_by(
        team_id=team.id,
        user_id=user.id,
    ).first()

    if existing_member:
        flash("You are already a member of this team.", "info")
        return redirect(url_for("auth.teams"))

    member_count = TeamMember.query.filter_by(team_id=team.id).count()

    if member_count >= team.max_members:
        flash("This team is already full.", "warning")
        return redirect(url_for("auth.teams"))

    join_request = TeamJoinRequest.query.filter_by(
        team_id=team.id,
        user_id=user.id,
    ).first()

    message = request.form.get("message", "").strip()

    if join_request and join_request.status == "pending":
        flash("You already have a pending request for this team.", "info")
        return redirect(url_for("auth.teams"))

    if join_request and join_request.status == "approved":
        flash("Your request was already approved.", "info")
        return redirect(url_for("auth.teams"))

    try:
        if join_request:
            join_request.status = "pending"
            join_request.message = message or None
            join_request.requested_at = datetime.now(timezone.utc)
            join_request.reviewed_at = None
        else:
            join_request = TeamJoinRequest(
                team_id=team.id,
                user_id=user.id,
                message=message or None,
                status="pending",
            )
            db.session.add(join_request)

        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        flash("Your request could not be submitted. Please try again.", "danger")
    else:
        flash("Your team join request has been submitted.", "success")

    return redirect(url_for("auth.teams"))


@auth.route("/teams/<int:team_id>/requests", methods=["GET"])
def team_join_requests(team_id):
    user = _get_active_user()

    if user is None:
        flash("Please log in to view team requests.", "warning")
        return redirect(url_for("auth.login"))

    team = db.session.get(Team, team_id)

    if team is None:
        flash("Team not found.", "danger")
        return redirect(url_for("auth.teams"))

    if team.created_by != user.id:
        flash("Only the team creator can review join requests.", "danger")
        return redirect(url_for("auth.teams"))

    requests_list = (
        db.session.query(TeamJoinRequest, User)
        .join(User, TeamJoinRequest.user_id == User.id)
        .filter(
            TeamJoinRequest.team_id == team.id,
            TeamJoinRequest.status == "pending",
        )
        .order_by(TeamJoinRequest.requested_at.asc())
        .all()
    )

    return render_template(
        "team_join_requests.html",
        team=team,
        requests=requests_list,
    )


@auth.route(
    "/teams/<int:team_id>/requests/<int:request_id>/<action>",
    methods=["POST"],
)
def review_team_request(team_id, request_id, action):
    user = _get_active_user()

    if user is None:
        flash("Please log in to review team requests.", "warning")
        return redirect(url_for("auth.login"))

    if action not in ("approve", "reject"):
        flash("Invalid request action.", "danger")
        return redirect(url_for("auth.teams"))

    team = db.session.get(Team, team_id)

    if team is None:
        flash("Team not found.", "danger")
        return redirect(url_for("auth.teams"))

    if team.created_by != user.id:
        flash("Only the team creator can review join requests.", "danger")
        return redirect(url_for("auth.teams"))

    join_request = db.session.get(TeamJoinRequest, request_id)

    if join_request is None or join_request.team_id != team.id:
        flash("Join request not found.", "danger")
        return redirect(url_for("auth.team_join_requests", team_id=team.id))

    if join_request.status != "pending":
        flash("This request has already been reviewed.", "warning")
        return redirect(url_for("auth.team_join_requests", team_id=team.id))

    if action == "approve":
        if team.status not in ("open", "active"):
            flash("This team is no longer accepting members.", "warning")
            return redirect(url_for("auth.team_join_requests", team_id=team.id))

        member_count = TeamMember.query.filter_by(team_id=team.id).count()

        if member_count >= team.max_members:
            flash("The team is full. This request cannot be approved.", "warning")
            return redirect(url_for("auth.team_join_requests", team_id=team.id))

        existing_member = TeamMember.query.filter_by(
            team_id=team.id,
            user_id=join_request.user_id,
        ).first()

        if existing_member:
            join_request.status = "approved"
            join_request.reviewed_at = datetime.now(timezone.utc)
        else:
            db.session.add(
                TeamMember(
                    team_id=team.id,
                    user_id=join_request.user_id,
                    role="member",
                )
            )
            join_request.status = "approved"
            join_request.reviewed_at = datetime.now(timezone.utc)

    else:
        join_request.status = "rejected"
        join_request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("The request could not be processed. Please try again.", "danger")
    else:
        flash(
            "Join request approved." if action == "approve"
            else "Join request rejected.",
            "success",
        )

    return redirect(url_for("auth.team_join_requests", team_id=team.id))


@auth.route("/teams/<int:team_id>/members", methods=["GET"])
def team_members(team_id):
    user = _get_active_user()

    if user is None:
        flash("Please log in to view team members.", "warning")
        return redirect(url_for("auth.login"))

    team = db.session.get(Team, team_id)

    if team is None:
        flash("Team not found.", "danger")
        return redirect(url_for("auth.teams"))

    is_member = TeamMember.query.filter_by(
        team_id=team.id,
        user_id=user.id,
    ).first() is not None

    if team.created_by != user.id and not is_member:
        flash("Only team members can view this team's members.", "danger")
        return redirect(url_for("auth.teams"))

    members = (
        db.session.query(TeamMember, User)
        .join(User, TeamMember.user_id == User.id)
        .filter(TeamMember.team_id == team.id)
        .order_by(TeamMember.joined_at.asc())
        .all()
    )

    return render_template(
        "team_members.html",
        team=team,
        members=members,
    )

@auth.route("/my-teams", methods=["GET"])
def my_teams():
    user = _get_active_user()

    if user is None:
        flash("Please log in to view your teams.", "warning")
        return redirect(url_for("auth.login"))

    # Teams where the user is a leader or approved member
    my_teams = (
        db.session.query(Team, Project, TeamMember)
        .join(Team, TeamMember.team_id == Team.id)
        .outerjoin(Project, Team.project_id == Project.id)
        .filter(TeamMember.user_id == user.id)
        .order_by(Team.created_at.desc())
        .all()
    )

    # Join request history for the current user
    my_requests = (
        db.session.query(TeamJoinRequest, Team, Project)
        .join(Team, TeamJoinRequest.team_id == Team.id)
        .outerjoin(Project, Team.project_id == Project.id)
        .filter(TeamJoinRequest.user_id == user.id)
        .order_by(TeamJoinRequest.requested_at.desc())
        .all()
    )

    return render_template(
        "my_teams.html",
        my_teams=my_teams,
        my_requests=my_requests,
    )

@auth.route(
    "/teams/<int:team_id>/requests/<int:request_id>/withdraw",
    methods=["POST"],
)
def withdraw_team_request(team_id, request_id):
    user = _get_active_user()

    if user is None:
        flash("Please log in to withdraw your join request.", "warning")
        return redirect(url_for("auth.login"))

    join_request = db.session.get(TeamJoinRequest, request_id)

    if (
        join_request is None
        or join_request.team_id != team_id
        or join_request.user_id != user.id
    ):
        flash("Join request not found.", "danger")
        return redirect(url_for("auth.my_teams"))

    if join_request.status != "pending":
        flash("Only pending requests can be withdrawn.", "warning")
        return redirect(url_for("auth.my_teams"))

    join_request.status = "withdrawn"
    join_request.reviewed_at = datetime.now(timezone.utc)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("Could not withdraw your request. Please try again.", "danger")
    else:
        flash("Your join request has been withdrawn.", "success")

    return redirect(url_for("auth.my_teams"))
