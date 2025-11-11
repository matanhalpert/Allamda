# Analytics Service

Interactive data visualization service for creating analytics dashboards using Plotly. Provides ready-to-use chart components for school performance metrics, student progress tracking, and trend analysis.

## Overview

The Analytics Service generates interactive, embeddable charts for school analytics dashboards. It uses Plotly to create professional, responsive visualizations with hover interactions, custom color schemes, and automatic handling of edge cases like missing data.

## Structure

```
analytics/
├── __init__.py     # Module exports
├── graphing.py     # GraphingService implementation
└── README.md       # This file
```

## Key Components

### GraphingService

Static service class providing chart generation methods. All methods return HTML strings that can be directly embedded in Jinja2 templates.

**Color Schemes:**
- **COLORS**: Bootstrap-style semantic colors (primary, success, warning, danger, info, secondary, light, dark)
- **LIGHT_COLORS**: Pastel color palette for multi-item charts (10 distinct colors)

## Available Chart Types

### 1. Bar Chart
```python
create_bar_chart(
    data: List[Dict],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str,
    y_label: str,
    color: Optional[str] = None
) -> str
```

Vertical bar chart with automatic color cycling. Displays values on bars and includes hover tooltips.

**Use Case**: Subject-wise performance, student count by grade, course enrollment

### 2. Line Chart
```python
create_line_chart(
    data: List[Dict],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str,
    y_label: str,
    color: Optional[str] = None
) -> str
```

Line chart with markers and hover interactions. Supports composite x-axis fields (e.g., year-month tuples).

**Use Case**: Performance trends over time, progress tracking

### 3. Horizontal Bar Chart
```python
create_horizontal_bar_chart(
    data: List[Dict],
    x_field: str,
    y_field: str,
    title: str,
    x_label: str,
    y_label: str,
    color: Optional[str] = None
) -> str
```

Horizontal bars with dynamic height based on number of items. Ideal for rankings and comparisons.

**Use Case**: Top students ranking, course difficulty comparison

### 4. Grade Trends Chart
```python
create_grade_trends_chart(
    trends_data: List[Dict]
) -> str
```

Specialized line chart for grade trends with filled area under the curve. Expects data with `year`, `month`, and `average_grade` fields.

**Use Case**: Student grade trends over academic year, class performance trends

### 5. Attendance Trends Chart
```python
create_attendance_trends_chart(
    trends_data: List[Dict]
) -> str
```

Specialized line chart for attendance rates. Expects data with `year`, `week`, and `attendance_rate` fields.

**Use Case**: Weekly attendance monitoring, absence pattern detection

### 6. Class Performance Chart
```python
create_class_performance_chart(
    class_data: List[Dict]
) -> str
```

Bar chart showing average grades by class. Expects data with `grade_level`, `year`, and `average_grade` fields.

**Use Case**: School-wide class comparison, grade level performance

### 7. Top Students Chart
```python
create_top_students_chart(
    students_data: List[Dict],
    limit: int = 10
) -> str
```

Horizontal bar chart highlighting top-performing students. Expects data with `name` and `average_grade` fields.

**Use Case**: Honor roll display, student recognition dashboards

## Usage

### Basic Usage in Routes

```python
from src.services.analytics import GraphingService

# In a route handler
@bp.route('/analytics')
def school_analytics():
    # Fetch data from database
    class_performance = [
        {'grade_level': '10th Grade', 'year': 2024, 'average_grade': 85.5},
        {'grade_level': '11th Grade', 'year': 2024, 'average_grade': 88.2},
        {'grade_level': '12th Grade', 'year': 2024, 'average_grade': 90.1}
    ]
    
    # Generate chart HTML
    chart_html = GraphingService.create_class_performance_chart(class_performance)
    
    # Pass to template
    return render_template('analytics.html', chart=chart_html)
```

### In Jinja2 Templates

```html
<!-- Template receives chart HTML as variable -->
<div class="chart-container">
    {{ chart|safe }}
</div>
```

### Custom Colors

```python
# Use specific color for all bars
chart = GraphingService.create_bar_chart(
    data=course_data,
    x_field='course_name',
    y_field='enrollment',
    title='Course Enrollment',
    x_label='Course',
    y_label='Number of Students',
    color='#007bff'  # Bootstrap primary blue
)

# Let service auto-assign different colors (pass None or omit)
chart = GraphingService.create_bar_chart(
    data=course_data,
    x_field='course_name',
    y_field='enrollment',
    title='Course Enrollment',
    x_label='Course',
    y_label='Number of Students'
    # color parameter omitted = multi-color bars
)
```

## Features

### Automatic Empty State Handling

All chart methods handle empty data gracefully:

```python
# If data is empty, returns a placeholder chart
chart = GraphingService.create_bar_chart(
    data=[],  # Empty data
    ...
)
# Returns: "No data available for this time period" message
```

### Responsive Design

- Charts are responsive and adapt to container width
- Dynamic heights for horizontal bar charts based on item count
- Mobile-friendly hover interactions

### Interactive Elements

- Hover tooltips with formatted values
- Clean, minimal design (display mode bar hidden)
- Unified hover mode for line charts (shows all series at x-position)

### Plotly Integration

- Uses CDN for Plotly.js (no local files needed)
- Generates standalone HTML div elements
- Template: `plotly_white` for clean, professional appearance

## Integration Points

### School Manager Routes
Used in `src/app/routes/school_manager.py` for:
- School-wide performance dashboards
- Class comparison analytics
- Trend analysis over time

### Class Manager Routes
Used in `src/app/routes/class_manager.py` for:
- Class-specific performance tracking
- Student ranking displays
- Attendance monitoring

### Parent Routes
Potential use in `src/app/routes/parent.py` for:
- Individual child progress charts
- Multi-child comparison views

### Templates
Charts embedded in:
- `school_analytics.html`: School-level dashboards
- `my_class.html`: Class manager analytics
- Custom analytics views

## Chart Customization

### Color Palette

The service provides two pre-defined color schemes:

**Semantic Colors (COLORS):**
- Primary: `#007bff` (blue)
- Success: `#28a745` (green)
- Warning: `#ffc107` (yellow)
- Danger: `#dc3545` (red)
- Info: `#17a2b8` (teal)
- Secondary: `#6c757d` (gray)

**Pastel Colors (LIGHT_COLORS):**
10 distinct pastel shades automatically cycled for multi-item charts.

### Layout Options

All charts use consistent layout settings:
- Height: 400px (except horizontal bars with dynamic height)
- Margins: 50px all sides (horizontal bars: left=150px for labels)
- Template: `plotly_white`
- Hover label styling: White background, dark text, clean borders

## Data Format Examples

### Bar/Line Chart Data
```python
data = [
    {'subject': 'Math', 'score': 85.5},
    {'subject': 'Science', 'score': 90.2},
    {'subject': 'History', 'score': 78.9}
]
```

### Trends Data (Grade)
```python
trends = [
    {'year': 2024, 'month': 9, 'average_grade': 82.5},
    {'year': 2024, 'month': 10, 'average_grade': 85.0},
    {'year': 2024, 'month': 11, 'average_grade': 87.2}
]
```

### Trends Data (Attendance)
```python
trends = [
    {'year': 2024, 'week': 1, 'attendance_rate': 95.5},
    {'year': 2024, 'week': 2, 'attendance_rate': 97.2},
    {'year': 2024, 'week': 3, 'attendance_rate': 94.8}
]
```

## Performance Considerations

- Charts are generated on-demand (not cached)
- Plotly.js loaded from CDN (reduces server bandwidth)
- HTML string generation is lightweight
- Consider pagination for large datasets (limit to 20-30 data points)

## Dependencies

- **Plotly**: Interactive charting library (`plotly.graph_objects`)
- **Python 3.7+**: Type hints support
- **Calendar module**: Month name formatting

## Notes

- All methods are static (no instance needed)
- Returns HTML strings ready for template embedding
- No database access (data provided by route handlers)
- Display mode bar hidden for cleaner appearance
- Charts use `|safe` filter in Jinja2 to render HTML

## Future Enhancements

Potential additions:
- Pie charts for distribution analysis
- Stacked bar charts for multi-dimensional data
- Heatmaps for time-series patterns
- Export functionality (PNG, PDF)
- Configurable themes (dark mode support)
- Animation for trend charts
- Drill-down interactivity

---

**Author**: Allamda Development Team  
**Last Updated**: November 2025  
**Version**: 1.0

