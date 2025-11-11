"""
Graphing service for creating analytics visualizations using Plotly.

This service handles the generation of interactive charts and visualizations
for school analytics dashboards.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import List, Dict, Optional
import calendar


class GraphingService:
    """Service for creating Plotly charts and visualizations."""

    COLORS = {
        'primary': '#007bff',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545',
        'info': '#17a2b8',
        'secondary': '#6c757d',
        'light': '#f8f9fa',
        'dark': '#343a40'
    }

    LIGHT_COLORS = [
        '#A8D5E2',  # Light blue
        '#B8E6B8',  # Light green
        '#FFD9A3',  # Light orange
        '#F9C4D2',  # Light pink
        '#C9B8E6',  # Light purple
        '#FFE4B5',  # Light peach
        '#B3E5D9',  # Light mint
        '#FFB6C1',  # Light rose
        '#D4E4BC',  # Light lime
        '#E0BBE4',  # Light lavender
    ]
    
    @staticmethod
    def create_bar_chart(
        data: List[Dict],
        x_field: str,
        y_field: str,
        title: str,
        x_label: str,
        y_label: str,
        color: Optional[str] = None
    ) -> str:
        """
        Create a bar chart and return it as HTML.

        Returns:
            HTML string of the chart
        """
        if not data:
            return GraphingService._create_no_data_chart(title)
        
        x_values = [item[x_field] for item in data]
        y_values = [item[y_field] for item in data]
        
        # Use different colors for each bar if no color specified
        if color:
            colors = color
        else:
            colors = [GraphingService.LIGHT_COLORS[i % len(GraphingService.LIGHT_COLORS)] for i in range(len(data))]
        
        fig = go.Figure(data=[
            go.Bar(
                x=x_values,
                y=y_values,
                marker_color=colors,
                text=y_values,
                textposition='auto',
                hovertemplate=f'<b>%{{x}}</b><br>{y_label}: %{{y:.1f}}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_line_chart(
        data: List[Dict],
        x_field: str,
        y_field: str,
        title: str,
        x_label: str,
        y_label: str,
        color: Optional[str] = None
    ) -> str:
        """
        Create a line chart and return it as HTML.

        Returns:
            HTML string of the chart
        """
        if not data:
            return GraphingService._create_no_data_chart(title)
        
        # Handle composite x-axis (e.g., year-month or year-week)
        if isinstance(x_field, tuple):
            x_values = [f"{item[x_field[0]]}-{str(item[x_field[1]]).zfill(2)}" for item in data]
        else:
            x_values = [item[x_field] for item in data]
        
        y_values = [item[y_field] if item[y_field] is not None else 0 for item in data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                line=dict(color=color or GraphingService.COLORS['info'], width=3),
                marker=dict(size=8),
                text=[f"{y:.1f}" if y is not None else "N/A" for y in y_values],
                hovertemplate='%{text}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_horizontal_bar_chart(
        data: List[Dict],
        x_field: str,
        y_field: str,
        title: str,
        x_label: str,
        y_label: str,
        color: Optional[str] = None
    ) -> str:
        """
        Create a horizontal bar chart (useful for rankings).

        Returns:
            HTML string of the chart
        """
        if not data:
            return GraphingService._create_no_data_chart(title)

        data_reversed = list(reversed(data))
        x_values = [item[x_field] for item in data_reversed]
        y_values = [item[y_field] for item in data_reversed]
        
        # Use different colors for each bar if no color specified
        if color:
            colors = color
        else:
            colors = [GraphingService.LIGHT_COLORS[i % len(GraphingService.LIGHT_COLORS)] for i in range(len(data_reversed))]
        
        fig = go.Figure(data=[
            go.Bar(
                x=x_values,
                y=y_values,
                orientation='h',
                marker_color=colors,
                text=x_values,
                textposition='auto',
                hovertemplate=f'<b>%{{y}}</b><br>{x_label}: %{{x:.1f}}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title=title,
            xaxis_title=x_label,
            yaxis_title=y_label,
            template='plotly_white',
            height=max(300, len(data) * 40),  # Dynamic height based on number of items
            margin=dict(l=150, r=50, t=50, b=50),
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_grade_trends_chart(trends_data: List[Dict]) -> str:
        """Create a line chart for grade trends over time.
        
        Args:
            trends_data: List of dicts with 'year', 'month', 'average_grade'
            
        Returns:
            HTML string of the chart
        """
        if not trends_data:
            return GraphingService._create_no_data_chart("Grade Trends Over Time")

        x_values = [
            f"{calendar.month_abbr[item['month']]} {item['year']}" 
            for item in trends_data
        ]
        y_values = [item['average_grade'] for item in trends_data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                line=dict(color=GraphingService.COLORS['primary'], width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor=f"rgba(0, 123, 255, 0.1)",
                text=[f"{y:.1f}" if y is not None else "N/A" for y in y_values],
                hovertemplate='Average Grade: %{text}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Grade Trends Over Time",
            xaxis_title="Month",
            yaxis_title="Average Grade",
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            yaxis=dict(range=[0, 100]),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_attendance_trends_chart(trends_data: List[Dict]) -> str:
        """Create a line chart for attendance trends over time.
        
        Args:
            trends_data: List of dicts with 'year', 'week', 'attendance_rate'
            
        Returns:
            HTML string of the chart
        """
        if not trends_data:
            return GraphingService._create_no_data_chart("Attendance Trends Over Time")

        x_values = [f"W{item['week']} {item['year']}" for item in trends_data]
        y_values = [item['attendance_rate'] for item in trends_data]
        
        fig = go.Figure(data=[
            go.Scatter(
                x=x_values,
                y=y_values,
                mode='lines+markers',
                line=dict(color=GraphingService.COLORS['success'], width=3),
                marker=dict(size=8),
                fill='tozeroy',
                fillcolor=f"rgba(40, 167, 69, 0.1)",
                text=[f"{y:.1f}%" if y is not None else "N/A" for y in y_values],
                hovertemplate='Attendance Rate: %{text}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Attendance Trends Over Time",
            xaxis_title="Week",
            yaxis_title="Attendance Rate (%)",
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            yaxis=dict(range=[0, 100]),
            hovermode='x unified',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_class_performance_chart(class_data: List[Dict]) -> str:
        """Create a bar chart for average grades by class.
        
        Args:
            class_data: List of dicts with 'grade_level', 'year', 'average_grade'
            
        Returns:
            HTML string of the chart
        """
        if not class_data:
            return GraphingService._create_no_data_chart("Average Grades by Class")

        labels = [f"{item['grade_level']} ({item['year']})" for item in class_data]
        grades = [item['average_grade'] if item['average_grade'] is not None else 0 for item in class_data]

        colors = [GraphingService.LIGHT_COLORS[i % len(GraphingService.LIGHT_COLORS)] for i in range(len(class_data))]
        
        fig = go.Figure(data=[
            go.Bar(
                x=labels,
                y=grades,
                marker_color=colors,
                text=[f"{g:.1f}" if g > 0 else "N/A" for g in grades],
                textposition='auto',
                hovertemplate='<b>%{x}</b><br>Average Grade: %{y:.1f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Average Grades by Class",
            xaxis_title="Class",
            yaxis_title="Average Grade",
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            yaxis=dict(range=[0, 100]),
            hovermode='closest',
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Arial",
                font_color="#333",
                bordercolor="#ddd"
            )
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
    
    @staticmethod
    def create_top_students_chart(students_data: List[Dict], limit: int = 10) -> str:
        """Create a horizontal bar chart for top students.
        
        Args:
            students_data: List of dicts with 'name', 'average_grade'
            limit: Number of students to show
            
        Returns:
            HTML string of the chart
        """
        if not students_data:
            return GraphingService._create_no_data_chart("Top Performing Students")

        top_students = students_data[:limit]
        
        return GraphingService.create_horizontal_bar_chart(
            data=top_students,
            x_field='average_grade',
            y_field='name',
            title=f"Top {len(top_students)} Performing Students",
            x_label="Average Grade",
            y_label="Student",
            color=None  # Use different colors per bar
        )
    
    @staticmethod
    def _create_no_data_chart(title: str) -> str:
        """
        Create a placeholder chart when no data is available.

        Returns:
            HTML string of the placeholder
        """
        fig = go.Figure()
        
        fig.add_annotation(
            text="No data available for this time period",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=16, color=GraphingService.COLORS['secondary'])
        )
        
        fig.update_layout(
            title=title,
            template='plotly_white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        
        return fig.to_html(include_plotlyjs='cdn', div_id=None, config={'displayModeBar': False})
