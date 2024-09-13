import streamlit as st
from app.database.db import execute_query
from datetime import datetime, timedelta
from app.events.event_management import get_all_categories
from app.search.search_engine import advanced_search, get_categories, get_content_providers, get_tags
from app.events.event_management import get_event_categories

def get_all_events(search_query=None, start_date=None, end_date=None, min_price=None, max_price=None, categories=None):
    query = """
    SELECT DISTINCT e.*, u.username as content_provider_name
    FROM events e
    JOIN users u ON e.content_provider_id = u.id
    LEFT JOIN event_categories ec ON e.id = ec.event_id
    WHERE e.is_published = TRUE
    """
    params = []

    if search_query:
        query += " AND (e.title LIKE %s OR e.description LIKE %s)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])

    if start_date:
        query += " AND e.start_time >= %s"
        params.append(start_date)

    if end_date:
        query += " AND e.end_time <= %s"
        params.append(end_date)

    if min_price is not None:
        query += " AND e.price >= %s"
        params.append(min_price)

    if max_price is not None:
        query += " AND e.price <= %s"
        params.append(max_price)

    if categories:
        query += " AND ec.category_id IN %s"
        params.append(tuple(categories))

    query += " ORDER BY e.start_time ASC"

    return execute_query(query, tuple(params))

def event_browser():
    st.header("Event Browser")

    user_role = st.session_state.get('user', {}).get('role')

    # Search and filter options
    search_query = st.text_input("Search events", "")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", datetime.now().date())
    with col2:
        end_date = st.date_input("End date", datetime.now().date() + timedelta(days=30))
    
    col3, col4 = st.columns(2)
    with col3:
        min_price = st.number_input("Min price", min_value=0.0, value=0.0, step=1.0)
    with col4:
        max_price = st.number_input("Max price", min_value=0.0, value=1000.0, step=1.0)

    # Category and tag filters
    categories = get_categories()
    tags = get_tags()
    
    col5, col6 = st.columns(2)
    with col5:
        selected_categories = st.multiselect("Filter by categories", options=[cat['name'] for cat in categories] if categories else [])
    with col6:
        selected_tags = st.multiselect("Filter by tags", options=[tag['name'] for tag in tags] if tags else [])

    category_ids = [cat['id'] for cat in categories if cat['name'] in selected_categories]
    tag_ids = [tag['id'] for tag in tags if tag['name'] in selected_tags]

    # Content provider filter
    content_providers = get_content_providers()
    selected_provider = st.selectbox("Filter by content provider", options=["All"] + [cp['username'] for cp in content_providers])
    content_provider = None if selected_provider == "All" else selected_provider

    # Sorting options
    col7, col8 = st.columns(2)
    with col7:
        sort_options = {
            "Start Date": "start_time",
            "Price": "price",
            "Average Rating": "avg_rating",
            "Number of Ratings": "total_ratings"
        }
        sort_by = st.selectbox("Sort by", options=list(sort_options.keys()))
    with col8:
        sort_order = st.radio("Sort order", options=["Ascending", "Descending"])

    # Pagination
    col9, col10 = st.columns(2)
    with col9:
        page = st.number_input("Page", min_value=1, value=1, step=1)
    with col10:
        per_page = st.number_input("Items per page", min_value=5, max_value=50, value=10, step=5)

    # Fetch and display events
    events, total_count = advanced_search(
        search_query=search_query,
        start_date=start_date,
        end_date=end_date,
        min_price=min_price,
        max_price=max_price,
        categories=category_ids,
        tags=tag_ids,
        content_provider=content_provider,
        sort_by=sort_options[sort_by],
        sort_order="ASC" if sort_order == "Ascending" else "DESC",
        page=page,
        per_page=per_page
    )

    st.write(f"Showing {len(events)} of {total_count} events")

    if not events:
        st.write("No events found matching your criteria.")
    else:
        for event in events:
            with st.expander(f"{event['title']} - {event['start_time']}"):
                st.write(f"Description: {event['description']}")
                st.write(f"Content Provider: {event['content_provider_name']}")
                st.write(f"Start: {event['start_time']}")
                st.write(f"End: {event['end_time']}")
                st.write(f"Price: ${event['price']}")
                avg_rating = event.get('avg_rating', 0)
                rating_count = event.get('rating_count', 0)
                st.write(f"Rating: {avg_rating:.2f} ({rating_count} ratings)")
                
                event_categories = get_event_categories(event['id'])
                st.write("Categories: " + ", ".join([cat['name'] for cat in event_categories]))
                
                col1, col2 = st.columns(2)
                with col1:
                    if user_role in ['admin', 'content_manager']:
                        if st.button(f"Edit Event", key=f"edit_event_{event['id']}"):
                            st.session_state['edit_event_id'] = event['id']
                            st.rerun()
                with col2:
                    if st.button(f"View Event", key=f"view_event_{event['id']}"):
                        st.session_state['view_event_id'] = event['id']
                        st.rerun()

    # Pagination controls
    total_pages = (total_count - 1) // per_page + 1
    st.write(f"Page {page} of {total_pages}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Previous Page", disabled=page==1):
            st.session_state['page'] = page - 1
            st.rerun()
    with col2:
        if st.button("Next Page", disabled=page==total_pages):
            st.session_state['page'] = page + 1
            st.rerun()
