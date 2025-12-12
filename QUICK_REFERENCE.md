# Quick Reference Card

## Common Commands

### Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Access Application
```
http://localhost:8000/rewards/
```

## View to URL Mapping

| View | URL Pattern | Method |
|------|-------------|--------|
| RewardList | `/rewards/` | GET |
| RewardDetail | `/rewards/{id}/` | GET |
| AddReward | `/rewards/add/` | GET/POST |
| UpdateReward | `/rewards/{id}/update/` | GET/POST |
| DeleteReward | `/rewards/{id}/delete/` | POST (with confirm) |
| RewardedList | `/rewards/rewarded/` | GET |
| RewardedDetail | `/rewards/rewarded/{id}/` | GET (login required) |
| AddRewarded | `/rewards/rewarded/add/` | GET/POST (login required) |
| Selection | `/rewards/selection/` | GET/POST (login required) |

## Authentication Requirements

| Feature | Requires Login |
|---------|---|
| View Rewards | ❌ No |
| Create Reward | ❌ No |
| Update Reward | ❌ No |
| Delete Reward | ❌ No |
| View Redeemed Rewards | ❌ No (list view) |
| View Single Redeemed Reward | ✅ Yes |
| Create Redeemed Reward | ✅ Yes |
| Redeem Reward (Selection) | ✅ Yes |

## Form Error Handling

All forms that handle POST requests provide user feedback:
- ✅ AddReward - Form validation with error messages
- ✅ UpdateReward - Form validation with error messages
- ✅ AddRewarded - Form validation with error messages
- ✅ Selection - Input validation with error messages

## Context Variables in Templates

| Template | Variable Name | Type |
|----------|---------------|------|
| reward_list.html | `rewards` | QuerySet |
| reward_detail.html | `reward` | Object |
| add_reward.html | `form` | Form |
| update_reward.html | `form`, `reward` | Form, Object |
| reward_confirm_delete.html | `object` | Object |
| rewarded_list.html | `rewarded_items` | QuerySet |
| rewarded_detail.html | `rewarded` | Object |
| add_rewarded.html | `form` | Form |
| selection.html | `rewards` | QuerySet |

## Fixed Issues Checklist

1. ✅ **Wrong View Inheritance** - All views use correct base classes
2. ✅ **Unsafe URL Parsing** - Using self.kwargs instead of request.path.split()
3. ✅ **Hard-coded Redirects** - All use reverse_lazy() with named URLs
4. ✅ **Missing Authentication** - LoginRequiredMixin on sensitive views
5. ✅ **Missing Form Error Handling** - form_invalid() methods with messages
6. ✅ **DeleteView Issues** - Standard Django pattern with confirmation
7. ✅ **Context Naming** - Consistent context_object_name across all views

## Key Files

| File | Purpose |
|------|---------|
| `rewards/views.py` | Main views (all fixed) |
| `rewards/urls.py` | Named URL patterns |
| `rewards/forms.py` | Form classes |
| `rewards/models.py` | Database models |
| `config/settings.py` | Django configuration |
| `templates/base.html` | Base template with styling |

## Important URL Names

Use these in templates with `{% url 'name' %}`:
- `reward-list` - List all rewards
- `reward-detail` - View single reward
- `reward-add` - Create new reward
- `reward-update` - Edit reward
- `reward-delete` - Delete reward
- `rewarded-list` - List redeemed rewards
- `rewarded-detail` - View redeemed reward
- `rewarded-add` - Create redeemed record
- `selection` - Redeem a reward

## Model Fields

### Reward
```python
title          # CharField(max_length=200)
description    # TextField
points_required # IntegerField
created_at     # DateTimeField (auto)
```

### Rewarded
```python
reward         # ForeignKey(Reward)
user           # ForeignKey(User)
redeemed_at    # DateTimeField (auto)
```

## Django Best Practices Used

✅ DetailView instead of ListView for single objects
✅ CreateView/UpdateView for forms
✅ reverse_lazy() for hardcoded URLs
✅ LoginRequiredMixin for authentication
✅ form_invalid() for error handling
✅ context_object_name for clarity
✅ Named URL patterns
✅ Django messages framework
✅ Django forms instead of manual HTML
✅ Django admin for database management

## Testing Tips

1. Test unauthenticated access to protected views (should redirect to login)
2. Submit invalid forms and verify error messages display
3. Test form success redirects work correctly
4. Verify Delete confirmation page appears before deletion
5. Check that URL names resolve correctly in templates
6. Test that context variables have correct names in templates
7. Verify CSRF tokens are present in all forms

## Debugging

### Check URL patterns
```python
python manage.py show_urls
```

### Interactive shell
```python
python manage.py shell
>>> from rewards.models import Reward
>>> Reward.objects.all()
```

### View registered URLs
In Django shell:
```python
from django.urls import reverse
reverse('reward-list')  # Test URL name resolution
```

## Deployment Checklist

- [ ] Set DEBUG = False in settings.py
- [ ] Set ALLOWED_HOSTS correctly
- [ ] Use environment variables for SECRET_KEY
- [ ] Use production database (not SQLite)
- [ ] Run collectstatic for static files
- [ ] Set up HTTPS/SSL
- [ ] Configure email for messages
- [ ] Run security checks: `python manage.py check --deploy`

---

**Status**: ✅ All 7 issues fixed and documented
