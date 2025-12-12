# Django Rewards Management System - Refactored

This is a Django application for managing rewards and tracking redeemed rewards. The codebase has been refactored to follow Django best practices and fix architectural and security issues.

## Architecture Overview

### Models

- **Reward**: Represents an available reward with title, description, and points required
- **Rewarded**: Tracks when a user redeems a reward

### Views

All views have been refactored to follow Django best practices:

#### Reward Views

- **RewardList** (ListView): Lists all available rewards
- **RewardDetail** (DetailView): Shows details of a single reward
- **AddReward** (CreateView): Creates a new reward with form validation and error handling
- **UpdateReward** (UpdateView): Updates an existing reward with proper success URL handling
- **DeleteReward** (DeleteView): Deletes a reward with confirmation

#### Rewarded Views

- **RewardedList** (ListView): Lists all redeemed rewards
- **RewardedDetail** (LoginRequiredMixin + DetailView): Shows details of a redeemed reward (requires authentication)
- **AddRewarded** (LoginRequiredMixin + CreateView): Creates a new rewarded record with form validation
- **Selection** (LoginRequiredMixin + ListView): Allows authenticated users to select and redeem rewards

## Key Refactoring Changes

### 1. Fixed View Inheritance
- Replaced `ListView` with `CreateView` for `AddReward` and `AddRewarded`
- Replaced `ListView` with `DetailView` for `RewardDetail` and `RewardedDetail`
- Replaced `UpdateView` manual implementation with proper `UpdateView` inheritance

### 2. Unsafe URL Parsing → URL Kwargs
- **Before**: `request.path.split('/')` - fragile and error-prone
- **After**: Using `self.kwargs.get('pk')` automatically provided by Django's DetailView and UpdateView

### 3. Hard-coded Redirects → reverse_lazy()
- **Before**: `redirect('/rewards/...')` - brittle, hardcoded URLs
- **After**: Using `reverse_lazy()` with named URL patterns for maintainability
- Example: `success_url = reverse_lazy('reward-list')`

### 4. Authentication
- Added `LoginRequiredMixin` to:
  - `RewardedDetail`
  - `AddRewarded`
  - `Selection`
- Ensures only authenticated users can access these views

### 5. Form Error Handling
- Implemented `form_invalid()` method to provide user feedback
- Displays error messages using Django's messages framework
- Renders template with form errors instead of silent redirects
- **Before**: Silent redirects on form errors
- **After**: Users see validation errors and can correct them

### 6. DeleteView Improvements
- Uses standard Django `DeleteView` pattern
- No custom `post()` overrides needed
- Provides confirmation template
- Clean `success_url` configuration with `reverse_lazy()`

### 7. Context Object Naming
- Consistent use of `context_object_name` across all views
- Removed conflicting variable names
- Clear, descriptive context variable names:
  - `rewards` for reward list
  - `reward` for single reward
  - `rewarded_items` for rewarded list
  - `rewarded` for single rewarded item

## URL Patterns

```
/rewards/                           - List all rewards (RewardList)
/rewards/<int:pk>/                  - View reward detail (RewardDetail)
/rewards/add/                       - Create new reward (AddReward)
/rewards/<int:pk>/update/           - Update reward (UpdateReward)
/rewards/<int:pk>/delete/           - Delete reward (DeleteReward)
/rewards/rewarded/                  - List redeemed rewards (RewardedList)
/rewards/rewarded/<int:pk>/         - View rewarded detail (RewardedDetail)
/rewards/rewarded/add/              - Create rewarded record (AddRewarded)
/rewards/selection/                 - Select reward to redeem (Selection)
```

## Running the Application

### Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Database

```bash
python manage.py migrate
python manage.py createsuperuser
```

### Run Server

```bash
python manage.py runserver
```

Visit `http://localhost:8000/rewards/` to access the application.

## Files

- `views.py`: Refactored views with all issues fixed
- `views_original.py`: Original views with issues (for reference)
- `urls.py`: Named URL patterns
- `models.py`: Reward and Rewarded models
- `forms.py`: Django forms for models
- `admin.py`: Django admin configuration
- `templates/`: HTML templates for all views

## Testing

The refactored views can be tested by:

1. Running the Django development server
2. Creating test data through the admin interface
3. Testing each view endpoint
4. Verifying form validation and error messages
5. Verifying authentication redirects on protected views
