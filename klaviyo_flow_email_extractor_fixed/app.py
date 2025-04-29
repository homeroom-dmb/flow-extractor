"""
Klaviyo Flow Email HTML Extractor

A Streamlit web application that helps you identify flow emails in Klaviyo 
and extract/render their HTML creative content.
"""
import streamlit as st
import os
import sys

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import utility functions
from klaviyo_api import (
    klaviyo_api_request, get_flows, get_flow_actions, 
    get_email_content, get_flow_metrics, get_message_metrics
)
from html_utils import extract_and_render_html, analyze_html_structure, check_email_compatibility

# Set page configuration
st.set_page_config(
    page_title="Klaviyo Flow Email HTML Extractor",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main Header
st.title("Klaviyo Flow Email HTML Extractor")
st.markdown("""
This app helps you identify flow emails in Klaviyo and extract/render their HTML creative content.
Use the sidebar to authenticate and navigate through the app's features.
""")

# Sidebar for authentication
with st.sidebar:
    st.header("Authentication")
    
    # Check for stored API key in session state
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    
    # Get API key from user
    api_key = st.text_input(
        "Enter your Klaviyo Private API Key:",
        value=st.session_state.api_key,
        type="password",
        key="api_key_input"
    )
    
    # Save API key to session state when updated
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    
    # Display connection status
    if api_key:
        try:
            test_response = klaviyo_api_request("flows", api_key, params={"page[size]": 1})
            if test_response and "data" in test_response:
                st.success("✅ Connected to Klaviyo")
                st.session_state.is_authenticated = True
            else:
                st.error("❌ Failed to connect to Klaviyo")
                st.session_state.is_authenticated = False
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")
            st.session_state.is_authenticated = False
    else:
        st.warning("⚠️ Please enter your Klaviyo API key")
        st.session_state.is_authenticated = False
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")
    
    # Only show navigation options if authenticated
    if st.session_state.get('is_authenticated', False):
        navigation = st.sidebar.radio(
            "Select a feature:",
            [
                "Flow Browser",
                "Email Extractor",
                "Template Analysis",
                "Bulk Operations"
            ]
        )
    else:
        navigation = "Welcome"

# Main content based on navigation
if navigation == "Welcome" or not st.session_state.get('is_authenticated', False):
    st.header("Welcome to Klaviyo Flow Email HTML Extractor")
    
    st.markdown("""
    To get started, please enter your Klaviyo Private API Key in the sidebar.
    
    ### Features
    
    * **Flow Browser**: View all your Klaviyo flows and their details
    * **Email Extractor**: Extract HTML content from flow emails
    * **Template Analysis**: Analyze email templates for best practices
    * **Bulk Operations**: Perform operations on multiple emails or flows
    
    ### Getting your Klaviyo API Key
    
    1. Log in to your Klaviyo account
    2. Go to Account → Settings → API Keys
    3. Create a Private API Key with appropriate permissions
    4. Copy the key and paste it in the sidebar
    
    ### Security Note
    
    Your API key is stored only in your browser's session and is not saved on any server.
    Always keep your API keys secure and don't share them with others.
    """)

elif navigation == "Flow Browser":
    st.header("Flow Browser")
    
    # Get all flows
    with st.spinner("Loading flows..."):
        flows_data = get_flows(st.session_state.api_key)
    
    if flows_data and "data" in flows_data:
        # Create a dataframe of flows
        flow_list = []
        
        for flow in flows_data["data"]:
            if flow.get("type") == "flow":
                flow_id = flow.get("id")
                attributes = flow.get("attributes", {})
                
                flow_info = {
                    "ID": flow_id,
                    "Name": attributes.get("name", "Unnamed Flow"),
                    "Status": attributes.get("status", "Unknown"),
                    "Created": attributes.get("created", "Unknown"),
                    "Updated": attributes.get("updated", "Unknown"),
                    "Trigger Type": attributes.get("trigger_type", "Unknown")
                }
                
                flow_list.append(flow_info)
        
        import pandas as pd
        flows_df = pd.DataFrame(flow_list)
        
        # Display the flows
        st.dataframe(flows_df, use_container_width=True)
        
        # Flow details section
        st.subheader("Flow Details")
        
        selected_flow_id = st.selectbox(
            "Select a flow to view details:",
            options=flows_df["ID"].tolist(),
            format_func=lambda x: flows_df[flows_df["ID"] == x]["Name"].iloc[0]
        )
        
        if selected_flow_id:
            with st.spinner("Loading flow details..."):
                # Get flow actions
                flow_actions = get_flow_actions(selected_flow_id, st.session_state.api_key)
                
                # Get flow metrics
                try:
                    flow_metrics = get_flow_metrics(selected_flow_id, st.session_state.api_key)_id, st.session_state.api_key)
                except Exception:
                    flow_metrics = None
                
                # Display flow details
                flow_name = flows_df[flows_df["ID"] == selected_flow_id]["Name"].iloc[0]
                st.subheader(f"Flow: {flow_name}")
                
                # Display flow actions in an expandable section
                if flow_actions:
                    with st.expander("Flow Actions", expanded=True):
                        # Create DataFrame of actions
                        action_list = []
                        
                        for action in flow_actions:
                            action_id = action.get("id")
                            attributes = action.get("attributes", {})
                            
                            action_info = {
                                "ID": action_id,
                                "Name": attributes.get("name", "Unnamed Action"),
                                "Type": attributes.get("action_type", "Unknown"),
                                "Status": attributes.get("status", "Unknown"),
                                "Created": attributes.get("created", "Unknown"),
                                "Updated": attributes.get("updated", "Unknown")
                            }
                            
                            action_list.append(action_info)
                        
                        actions_df = pd.DataFrame(action_list)
                        st.dataframe(actions_df, use_container_width=True)
                else:
                    st.info("No actions found for this flow.")
                
                # Display flow metrics if available
                if flow_metrics and "data" in flow_metrics:
                    with st.expander("Flow Metrics"):
                        st.json(flow_metrics)
                else:
                    st.info("No metrics available for this flow.")

elif navigation == "Email Extractor":
    st.header("Email HTML Extractor")
    
    # Get all flows for selection
    with st.spinner("Loading flows..."):
        flows_data = get_flows(st.session_state.api_key)
    
    if flows_data and "data" in flows_data:
        # Create flow options
        flow_options = {}
        for flow in flows_data["data"]:
            if flow.get("type") == "flow":
                flow_id = flow.get("id")
                flow_name = flow.get("attributes", {}).get("name", "Unnamed Flow")
                if flow_id and flow_name:
                    flow_options[flow_id] = flow_name
        
        if flow_options:
            # Get selected flow
            selected_flow = st.selectbox(
                "Select a Flow:",
                options=list(flow_options.values())
            )
            
            # Get flow ID from selected name
            selected_flow_id = None
            for flow_id, flow_name in flow_options.items():
                if flow_name == selected_flow:
                    selected_flow_id = flow_id
                    break
            
            if selected_flow_id:
                # Get email actions in the selected flow
                with st.spinner("Loading flow emails..."):
                    flow_actions = get_flow_actions(selected_flow_id, st.session_state.api_key)
                
                if flow_actions:
                    # Create options for email actions
                    email_options = {}
                    for action in flow_actions:
                        action_id = action.get("id")
                        action_name = action.get("attributes", {}).get("name", "Unnamed Email")
                        if action_id and action_name:
                            email_options[action_id] = action_name
                    
                    if email_options:
                        # Get selected email
                        selected_email = st.selectbox(
                            "Select an Email:",
                            options=list(email_options.values())
                        )
                        
                        # Get action ID from selected name
                        selected_action_id = None
                        for action_id, action_name in email_options.items():
                            if action_name == selected_email:
                                selected_action_id = action_id
                                break
                        
                        if selected_action_id:
                            # Get email content
                            with st.spinner("Loading email content..."):
                                email_message = get_email_content(selected_action_id, st.session_state.api_key)
                            
                            if email_message:
                                # Extract HTML content
                                html_content, formatted_html = extract_and_render_html(email_message)
                                
                                if html_content:
                                    st.success("Email HTML content loaded successfully!")
                                    
                                    # Display HTML content
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.subheader("HTML Preview")
                                        st.components.v1.html(html_content, height=600, scrolling=True)
                                    
                                    with col2:
                                        tabs = st.tabs(["HTML Source", "Template Info"])
                                        
                                        with tabs[0]:
                                            st.code(formatted_html, language="html")
                                        
                                        with tabs[1]:
                                            # Display template information
                                            template_info = email_message.get("attributes", {})
                                            subject = template_info.get("subject", "No subject")
                                            preview_text = template_info.get("preview_text", "No preview text")
                                            
                                            st.markdown(f"**Subject:** {subject}")
                                            st.markdown(f"**Preview Text:** {preview_text}")
                                            
                                            # Display other template attributes
                                            st.markdown("**Other Template Attributes:**")
                                            for key, value in template_info.items():
                                                if key not in ["html", "subject", "preview_text"]:
                                                    st.markdown(f"**{key}:** {value}")
                                    
                                    # Download button for HTML content
                                    st.download_button(
                                        label="Download HTML",
                                        data=html_content,
                                        file_name=f"{selected_email.replace(' ', '_')}.html",
                                        mime="text/html"
                                    )
                                else:
                                    st.warning("No HTML content found for this email.")
                            else:
                                st.error("Failed to fetch email content.")
                    else:
                        st.warning("No email actions found in this flow.")
                else:
                    st.warning("No actions found in this flow or there was an error fetching the flow actions.")
        else:
            st.warning("No flows found in your Klaviyo account.")
    else:
        st.warning("No flows found in your Klaviyo account, or there was an error fetching the flows.")

elif navigation == "Template Analysis":
    st.header("Email Template Analysis")
    
    # Two options: Analyze from flow or upload HTML
    analysis_option = st.radio(
        "Choose analysis source:",
        ["Analyze Flow Email", "Upload HTML File"]
    )
    
    html_content = None
    
    if analysis_option == "Analyze Flow Email":
        # Similar flow and email selection as in Email Extractor
        with st.spinner("Loading flows..."):
            flows_data = get_flows(st.session_state.api_key)
        
        if flows_data and "data" in flows_data:
            flow_options = {}
            for flow in flows_data["data"]:
                if flow.get("type") == "flow":
                    flow_id = flow.get("id")
                    flow_name = flow.get("attributes", {}).get("name", "Unnamed Flow")
                    if flow_id and flow_name:
                        flow_options[flow_id] = flow_name
            
            if flow_options:
                col1, col2 = st.columns(2)
                
                with col1:
                    selected_flow = st.selectbox(
                        "Select a Flow:",
                        options=list(flow_options.values())
                    )
                    
                    # Get flow ID from selected name
                    selected_flow_id = None
                    for flow_id, flow_name in flow_options.items():
                        if flow_name == selected_flow:
                            selected_flow_id = flow_id
                            break
                
                if selected_flow_id:
                    with st.spinner("Loading flow emails..."):
                        flow_actions = get_flow_actions(selected_flow_id, st.session_state.api_key)
                    
                    if flow_actions:
                        email_options = {}
                        for action in flow_actions:
                            action_id = action.get("id")
                            action_name = action.get("attributes", {}).get("name", "Unnamed Email")
                            if action_id and action_name:
                                email_options[action_id] = action_name
                        
                        if email_options:
                            with col2:
                                selected_email = st.selectbox(
                                    "Select an Email:",
                                    options=list(email_options.values())
                                )
                                
                                # Get action ID from selected name
                                selected_action_id = None
                                for action_id, action_name in email_options.items():
                                    if action_name == selected_email:
                                        selected_action_id = action_id
                                        break
                            
                            if selected_action_id and st.button("Analyze Template"):
                                with st.spinner("Loading and analyzing email content..."):
                                    email_message = get_email_content(selected_action_id, st.session_state.api_key)
                                    
                                    if email_message:
                                        # Extract HTML content
                                        html_content, _ = extract_and_render_html(email_message)
                                    else:
                                        st.error("Failed to fetch email content.")
                        else:
                            st.warning("No email actions found in this flow.")
                    else:
                        st.warning("No actions found in this flow.")
            else:
                st.warning("No flows found in your Klaviyo account.")
        else:
            st.warning("No flows found in your Klaviyo account, or there was an error fetching the flows.")
    
    elif analysis_option == "Upload HTML File":
        uploaded_file = st.file_uploader("Upload HTML File", type=["html", "htm"])
        
        if uploaded_file is not None:
            html_content = uploaded_file.getvalue().decode('utf-8')
            st.success("HTML file uploaded successfully!")
    
    # If we have HTML content from either source, analyze it
    if html_content:
        # Perform analysis
        with st.spinner("Analyzing template..."):
            # Get HTML structure analysis
            structure_analysis = analyze_html_structure(html_content)
            
            # Get email compatibility check
            compatibility = check_email_compatibility(html_content)
        
        # Display analysis results
        st.subheader("Analysis Results")
        
        # Create tabs for different analysis sections
        tabs = st.tabs([
            "Structure Analysis", 
            "Email Compatibility", 
            "Recommendations"
        ])
        
        with tabs[0]:
            # Structure Analysis
            st.subheader("HTML Structure")
            
            # Display key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Elements", structure_analysis["total_elements"])
            with col2:
                st.metric("Images", structure_analysis["elements"]["images"])
            with col3:
                st.metric("Links", structure_analysis["elements"]["links"])
            with col4:
                st.metric("Tables", structure_analysis["elements"]["tables"])
            
            # Display more detailed information
            with st.expander("Detailed Element Breakdown"):
                element_counts = structure_analysis["elements"]
                
                # Convert to DataFrame for better display
                import pandas as pd
                element_df = pd.DataFrame({
                    'Element Type': element_counts.keys(),
                    'Count': element_counts.values()
                })
                
                st.dataframe(element_df, use_container_width=True)
            
            # Image analysis
            if structure_analysis["elements"]["images"] > 0:
                with st.expander("Image Analysis"):
                    img_analysis = structure_analysis["images"]
                    
                    st.write(f"Total Images: {img_analysis['count']}")
                    st.write(f"Images with Alt Text: {img_analysis['with_alt_text']}")
                    st.write(f"Images without Alt Text: {img_analysis['without_alt_text']}")
                    st.write(f"Images with Width/Height: {img_analysis['with_width_height']}")
                    
                    # Calculate alt text percentage
                    alt_percentage = (img_analysis['with_alt_text'] / img_analysis['count']) * 100 if img_analysis['count'] > 0 else 0
                    st.progress(alt_percentage / 100, f"Alt Text Coverage: {alt_percentage:.1f}%")
            
            # Responsiveness analysis
            with st.expander("Responsiveness Analysis"):
                resp_analysis = structure_analysis["responsiveness"]
                
                if resp_analysis["has_media_queries"]:
                    st.success("✅ Template has media queries for responsive design")
                    st.write(f"Number of media queries: {resp_analysis['media_query_count']}")
                else:
                    st.warning("⚠️ Template does not have media queries")
                
                if resp_analysis["has_viewport_meta"]:
                    st.success("✅ Template has viewport meta tag")
                else:
                    st.warning("⚠️ Template does not have viewport meta tag")
                
                if resp_analysis["has_max_width"]:
                    st.success("✅ Template uses max-width for responsive sizing")
                else:
                    st.warning("⚠️ Template does not use max-width")
        
        with tabs[1]:
            # Email Compatibility
            st.subheader("Email Client Compatibility")
            
            # Display general compatibility info
            general = compatibility["general"]
            layout = compatibility["layout"]
            issues = compatibility["problematic_elements"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Structure")
                
                if general["has_doctype"]:
                    st.success("✅ Has DOCTYPE")
                else:
                    st.error("❌ Missing DOCTYPE")
                
                if layout["uses_tables_for_layout"]:
                    st.success("✅ Uses tables for layout (good for email)")
                else:
                    st.warning("⚠️ Not using tables for layout (may cause issues in some clients)")
                
                if general["uses_html5_elements"]:
                    st.warning("⚠️ Uses HTML5 elements (may not be supported in all email clients)")
                else:
                    st.success("✅ No HTML5 elements")
            
            with col2:
                st.write("### Potential Issues")
                
                issue_count = sum(1 for issue, has_issue in issues.items() if has_issue)
                
                if issue_count == 0:
                    st.success("✅ No potential compatibility issues found")
                else:
                    st.warning(f"⚠️ Found {issue_count} potential compatibility issues")
                    
                    for issue, has_issue in issues.items():
                        if has_issue:
                            st.write(f"❌ Has {issue.replace('_', ' ')}")
            
            # Display recommendations
            if compatibility["recommendations"]:
                st.subheader("Compatibility Recommendations")
                
                for i, rec in enumerate(compatibility["recommendations"], 1):
                    st.write(f"{i}. {rec}")
        
        with tabs[2]:
            # Recommendations
            st.subheader("Template Recommendations")
            
            # Generate recommendations based on analysis
            recommendations = []
            
            # Check for alt text
            img_analysis = structure_analysis["images"]
            if img_analysis["without_alt_text"] > 0:
                recommendations.append(f"Add alt text to {img_analysis['without_alt_text']} images for accessibility and when images are blocked")
            
            # Check for responsiveness
            resp_analysis = structure_analysis["responsiveness"]
            if not resp_analysis["has_media_queries"]:
                recommendations.append("Add media queries for better mobile responsiveness")
            
            # Check for potential compatibility issues
            for issue, has_issue in compatibility["problematic_elements"].items():
                if has_issue:
                    issue_name = issue.replace("has_", "").replace("_", " ")
                    recommendations.append(f"Remove {issue_name} as it may cause compatibility issues in some email clients")
            
            # Display recommendations
            if recommendations:
                for i, rec in enumerate(recommendations, 1):
                    st.write(f"{i}. {rec}")
            else:
                st.success("✅ No major issues found in template")

elif navigation == "Bulk Operations":
    st.header("Bulk Operations")
    
    # Select operation type
    operation_type = st.selectbox(
        "Select Operation Type:",
        [
            "Extract All HTML Templates from Flow",
            "Extract All HTML Templates from All Flows",
            "Generate Template Report"
        ]
    )
    
    if operation_type == "Extract All HTML Templates from Flow":
        # Get all flows
        with st.spinner("Loading flows..."):
            flows_data = get_flows(st.session_state.api_key)
        
        if flows_data and "data" in flows_data:
            # Create flow options
            flow_options = {}
            for flow in flows_data["data"]:
                if flow.get("type") == "flow":
                    flow_id = flow.get("id")
                    flow_name = flow.get("attributes", {}).get("name", "Unnamed Flow")
                    if flow_id and flow_name:
                        flow_options[flow_id] = flow_name
            
            if flow_options:
                # Select flow
                selected_flow = st.selectbox(
                    "Select a Flow:",
                    options=list(flow_options.values())
                )
                
                # Get flow ID from selected name
                selected_flow_id = None
                for flow_id, flow_name in flow_options.items():
                    if flow_name == selected_flow:
                        selected_flow_id = flow_id
                        break
                
                if selected_flow_id and st.button("Extract All Templates"):
                    with st.spinner("Extracting templates..."):
                        # Get flow actions
                        flow_actions = get_flow_actions(selected_flow_id, st.session_state.api_key)
                        
                        if flow_actions:
                            # Create a ZIP file with all HTML content
                            import io
                            import zipfile
                            
                            # Create in-memory ZIP file
                            zip_buffer = io.BytesIO()
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                # Add each email to the ZIP
                                for action in flow_actions:
                                    action_id = action.get("id")
                                    action_name = action.get("attributes", {}).get("name", "Unnamed Email")
                                    
                                    if action_id:
                                        # Get email content
                                        email_message = get_email_content(action_id, st.session_state.api_key)
                                        
                                        if email_message:
                                            # Extract HTML content
                                            html_content, _ = extract_and_render_html(email_message)
                                            
                                            if html_content:
                                                # Add to ZIP file
                                                filename = f"{action_name.replace(' ', '_')}.html"
                                                zip_file.writestr(filename, html_content)
                            
                            # Provide download button for ZIP file
                            zip_buffer.seek(0)
                            st.download_button(
                                label="Download All Templates (ZIP)",
                                data=zip_buffer,
                                file_name=f"{selected_flow}_templates.zip",
                                mime="application/zip"
                            )
                            
                            st.success("Templates extracted successfully!")
                        else:
                            st.warning("No email actions found in this flow.")
            else:
                st.warning("No flows found in your Klaviyo account.")
        else:
            st.warning("No flows found in your Klaviyo account, or there was an error fetching the flows.")
    
    elif operation_type == "Extract All HTML Templates from All Flows":
        if st.button("Extract All Templates from All Flows"):
            with st.spinner("Extracting templates from all flows..."):
                # Get all flows
                flows_data = get_flows(st.session_state.api_key)
                
                if flows_data and "data" in flows_data:
                    # Create in-memory ZIP file
                    import io
                    import zipfile
                    
                    zip_buffer = io.BytesIO()
                    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                        # Process each flow
                        for flow in flows_data["data"]:
                            if flow.get("type") == "flow":
                                flow_id = flow.get("id")
                                flow_name = flow.get("attributes", {}).get("name", "Unnamed Flow")
                                
                                if flow_id and flow_name:
                                    # Create directory for flow
                                    flow_dir = flow_name.replace(' ', '_')
                                    
                                    # Get flow actions
                                    flow_actions = get_flow_actions(flow_id, st.session_state.api_key)
                                    
                                    if flow_actions:
                                        # Add each email to the ZIP
                                        for action in flow_actions:
                                            action_id = action.get("id")
                                            action_name = action.get("attributes", {}).get("name", "Unnamed Email")
                                            
                                            if action_id:
                                                # Get email content
                                                email_message = get_email_content(action_id, st.session_state.api_key)
                                                
                                                if email_message:
                                                    # Extract HTML content
                                                    html_content, _ = extract_and_render_html(email_message)
                                                    
                                                    if html_content:
                                                        # Add to ZIP file
                                                        filename = f"{flow_dir}/{action_name.replace(' ', '_')}.html"
                                                        zip_file.writestr(filename, html_content)
                    
                    # Provide download button for ZIP file
                    zip_buffer.seek(0)
                    st.download_button(
                        label="Download All Templates (ZIP)",
                        data=zip_buffer,
                        file_name="all_flow_templates.zip",
                        mime="application/zip"
                    )
                    
                    st.success("All templates extracted successfully!")
                else:
                    st.warning("No flows found in your Klaviyo account, or there was an error fetching the flows.")
    
    elif operation_type == "Generate Template Report":
        # Get all flows
        with st.spinner("Loading flows..."):
            flows_data = get_flows(st.session_state.api_key)
        
        if flows_data and "data" in flows_data:
            # Create flow options
            flow_options = {}
            for flow in flows_data["data"]:
                if flow.get("type") == "flow":
                    flow_id = flow.get("id")
                    flow_name = flow.get("attributes", {}).get("name", "Unnamed Flow")
                    if flow_id and flow_name:
                        flow_options[flow_id] = flow_name
            
            if flow_options:
                # Multi-select for flows
                selected_flows = st.multiselect(
                    "Select Flows:",
                    options=list(flow_options.values())
                )
                
                if selected_flows and st.button("Generate Report"):
                    with st.spinner("Generating template report..."):
                        # Create list to store report data
                        report_data = []
                        
                        # Process each selected flow
                        for flow_name in selected_flows:
                            # Get flow ID
                            flow_id = None
                            for fid, fname in flow_options.items():
                                if fname == flow_name:
                                    flow_id = fid
                                    break
                            
                            if flow_id:
                                # Get flow actions
                                flow_actions = get_flow_actions(flow_id, st.session_state.api_key)
                                
                                if flow_actions:
                                    # Process each email action
                                    for action in flow_actions:
                                        action_id = action.get("id")
                                        action_name = action.get("attributes", {}).get("name", "Unnamed Email")
                                        
                                        if action_id:
                                            # Get email content
                                            email_message = get_email_content(action_id, st.session_state.api_key)
                                            
                                            if email_message:
                                                # Extract HTML content
                                                html_content, _ = extract_and_render_html(email_message)
                                                
                                                if html_content:
                                                    # Analyze template
                                                    structure = analyze_html_structure(html_content)
                                                    compatibility = check_email_compatibility(html_content)
                                                    
                                                    # Add to report data
                                                    report_item = {
                                                        "Flow": flow_name,
                                                        "Email": action_name,
                                                        "Elements": structure["total_elements"],
                                                        "Images": structure["elements"]["images"],
                                                        "Links": structure["elements"]["links"],
                                                        "Tables": structure["elements"]["tables"],
                                                        "Mobile Responsive": "Yes" if structure["responsiveness"]["has_media_queries"] else "No",
                                                        "Issues": len([i for i, v in compatibility["problematic_elements"].items() if v]),
                                                        "Recommendations": len(compatibility["recommendations"])
                                                    }
                                                    
                                                    report_data.append(report_item)
                        
                        # Create DataFrame from report data
                        if report_data:
                            import pandas as pd
                            report_df = pd.DataFrame(report_data)
                            
                            # Display report
                            st.subheader("Template Analysis Report")
                            st.dataframe(report_df, use_container_width=True)
                            
                            # Download report as CSV
                            csv = report_df.to_csv(index=False)
                            st.download_button(
                                label="Download Report (CSV)",
                                data=csv,
                                file_name="template_analysis_report.csv",
                                mime="text/csv"
                            )
                            
                            # Display summary statistics
                            with st.expander("Report Summary"):
                                st.write("### Template Statistics")
                                
                                total_templates = len(report_data)
                                responsive_templates = sum(1 for item in report_data if item["Mobile Responsive"] == "Yes")
                                avg_elements = sum(item["Elements"] for item in report_data) / total_templates if total_templates > 0 else 0
                                avg_images = sum(item["Images"] for item in report_data) / total_templates if total_templates > 0 else 0
                                
                                col1, col2, col3, col4 = st.columns(4)
                                
                                with col1:
                                    st.metric("Total Templates", total_templates)
                                with col2:
                                    st.metric("Responsive Templates", responsive_templates)
                                with col3:
                                    st.metric("Avg. Elements", f"{avg_elements:.1f}")
                                with col4:
                                    st.metric("Avg. Images", f"{avg_images:.1f}")
                                
                                # Create a bar chart for issues
                                st.write("### Issues by Template")
                                issues_chart_data = pd.DataFrame({
                                    'Template': [f"{item['Flow']}: {item['Email']}" for item in report_data],
                                    'Issues': [item['Issues'] for item in report_data]
                                })
                                st.bar_chart(issues_chart_data.set_index('Template'))
                        else:
                            st.warning("No template data found for the selected flows.")
                else:
                    st.info("Please select at least one flow and click 'Generate Report'")
            else:
                st.warning("No flows found in your Klaviyo account.")
        else:
            st.warning("No flows found in your Klaviyo account, or there was an error fetching the flows.")

# Add footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; opacity: 0.7; font-size: 0.9rem;">
        Klaviyo Flow Email HTML Extractor | Made with Streamlit | Deploy with GitHub
    </div>
    """,
    unsafe_allow_html=True
)
"""
Klaviyo Flow Email HTML Extractor

A Streamlit web application that helps you identify flow emails in Klaviyo 
and extract/render their HTML creative content.
"""
import streamlit as st
import os
import sys

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Import utility functions
from klaviyo_api import (
    klaviyo_api_request, get_flows, get_flow_actions, 
    get_email_content, get_flow_metrics, get_message_metrics
)
from html_utils import extract_and_render_html, analyze_html_structure, check_email_compatibility

# Set page configuration
st.set_page_config(
    page_title="Klaviyo Flow Email HTML Extractor",
    page_icon="✉️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main Header
st.title("Klaviyo Flow Email HTML Extractor")
st.markdown("""
This app helps you identify flow emails in Klaviyo and extract/render their HTML creative content.
Use the sidebar to authenticate and navigate through the app's features.
""")

# Sidebar for authentication
with st.sidebar:
    st.header("Authentication")
    
    # Check for stored API key in session state
    if 'api_key' not in st.session_state:
        st.session_state.api_key = ""
    
    # Get API key from user
    api_key = st.text_input(
        "Enter your Klaviyo Private API Key:",
        value=st.session_state.api_key,
        type="password",
        key="api_key_input"
    )
    
    # Save API key to session state when updated
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    
    # Display connection status
    if api_key:
        try:
            test_response = klaviyo_api_request("flows", api_key, params={"page[size]": 1})
            if test_response and "data" in test_response:
                st.success("✅ Connected to Klaviyo")
                st.session_state.is_authenticated = True
            else:
                st.error("❌ Failed to connect to Klaviyo")
                st.session_state.is_authenticated = False
        except Exception as e:
            st.error(f"❌ Connection Error: {str(e)}")
            st.session_state.is_authenticated = False
    else:
        st.warning("⚠️ Please enter your Klaviyo API key")
        st.session_state.is_authenticated = False
    
    # Navigation
    st.sidebar.markdown("---")
    st.sidebar.header("Navigation")
    
    # Only show navigation options if authenticated
    if st.session_state.get('is_authenticated', False):
        navigation = st.sidebar.radio(
            "Select a feature:",
            [
                "Flow Browser",
                "Email Extractor",
                "Template Analysis",
                "Bulk Operations"
            ]
        )
    else:
        navigation = "Welcome"

# Main content based on navigation
if navigation == "Welcome" or not st.session_state.get('is_authenticated', False):
    st.header("Welcome to Klaviyo Flow Email HTML Extractor")
    
    st.markdown("""
    To get started, please enter your Klaviyo Private API Key in the sidebar.
    
    ### Features
    
    * **Flow Browser**: View all your Klaviyo flows and their details
    * **Email Extractor**: Extract HTML content from flow emails
    * **Template Analysis**: Analyze email templates for best practices
    * **Bulk Operations**: Perform operations on multiple emails or flows
    
    ### Getting your Klaviyo API Key
    
    1. Log in to your Klaviyo account
    2. Go to Account → Settings → API Keys
    3. Create a Private API Key with appropriate permissions
    4. Copy the key and paste it in the sidebar
    
    ### Security Note
    
    Your API key is stored only in your browser's session and is not saved on any server.
    Always keep your API keys secure and don't share them with others.
    """)

elif navigation == "Flow Browser":
    st.header("Flow Browser")
    
    # Get all flows
    with st.spinner("Loading flows..."):
        flows_data = get_flows(st.session_state.api_key)
    
    if flows_data and "data" in flows_data:
        # Create a dataframe of flows
        flow_list = []
        
        for flow in flows_data["data"]:
            if flow.get("type") == "flow":
                flow_id = flow.get("id")
                attributes = flow.get("attributes", {})
                
                flow_info = {
                    "ID": flow_id,
                    "Name": attributes.get("name", "Unnamed Flow"),
                    "Status": attributes.get("status", "Unknown"),
                    "Created": attributes.get("created", "Unknown"),
                    "Updated": attributes.get("updated", "Unknown"),
                    "Trigger Type": attributes.get("trigger_type", "Unknown")
                }
                
                flow_list.append(flow_info)
        
        import pandas as pd
        flows_df = pd.DataFrame(flow_list)
        
        # Display the flows
        st.dataframe(flows_df, use_container_width=True)
        
        # Flow details section
        st.subheader("Flow Details")
        
        selected_flow_id = st.selectbox(
            "Select a flow to view details:",
            options=flows_df["ID"].tolist(),
            format_func=lambda x: flows_df[flows_df["ID"] == x]["Name"].iloc[0]
        )
        
        if selected_flow_id:
            with st.spinner("Loading flow details..."):
                # Get flow actions
                flow_actions = get_flow_actions(selected_flow_id, st.session_state.api_key)
                
                # Get flow metrics
                flow_metrics = get_flow_metrics(selected_flow_id, st.session_state.api_key)