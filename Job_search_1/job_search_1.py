import streamlit as st
import openai
from metaphor_python import Metaphor
import re

# Set OpenAI API key
openai.api_key = st.secrets['pass']

# Set Metaphor API key
metaphor = Metaphor(st.secrets['pass1'])

# App title
st.markdown("<h2 style='text-align: center;'> Job Search Assistant 🔍 </h2><p style='text-align: center; font-size: 18px;'>Goodbye to Experience-Level Uncertainity with LLMs and Metaphor API 👋</p>", unsafe_allow_html=True)

st.write("") 
st.write("")

# User input for the question
USER_QUESTION = st.text_input("Enter the job title:")



# USER_QUESTION = st.text_area("Enter job title:", height=50)

st.markdown("Sample Search: 'Job Title' Listings (e.g., New Data Scientist Positions / Data Scientist Jobs)")

num_postings = st.sidebar.slider("Number of Job Postings:", 5, 20, 10, step=5)

# Button to perform the search
if st.button("Search"):
    if USER_QUESTION:
        SYSTEM_MESSAGE = "You are a helpful assistant that generates search queries based on user questions. Only generate one search query."

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": USER_QUESTION},
            ],
        )

        query = completion.choices[0].message.content
        search_response = metaphor.search(
            query, num_results=num_postings, use_autoprompt=True, start_published_date="2023-08-15"
        )

        SYSTEM_MESSAGE = "Just give me the Company Name, Job Title, Years of Experience Required for the job"

        contents_result = search_response.get_contents()

        pattern = r"(\d+\.?\d*) (years|year)"

        # Initialize job ID counters for all postings and for displayed postings
        # Initialize job ID counters for displayed postings and total job postings
        job_id_displayed = 0
        total_job_postings = len(contents_result.contents)

        # Iterate through each link in the search results
        for i, link in enumerate(contents_result.contents):
            # Extract the content of the link
            link_content = link.extract

            if "linkedin.com" in link.url or "twitter.com" in link.url:
                # Skip LinkedIn and Twitter job postings
                total_job_postings -= 1
                continue

            # Increment the displayed job ID counter
            job_id_displayed += 1

            if job_id_displayed > num_postings:
                # Break the loop if the requested number of job postings has been displayed
                break

            # Use the link content as user input for OpenAI API
            messages = [
                {"role": "system", "content": SYSTEM_MESSAGE},
                {"role": "user", "content": link_content},
            ]

            # Make an API request for the current link
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            # Extract and display the response for the current link
            summary = completion.choices[0].message.content
            lines = summary.split('\n')
            
            # Extract and display URL, company, title, and experience
            url = link.url
            company = lines[0] if len(lines) > 0 else ""
            title = lines[1] if len(lines) > 1 else ""
            experience = lines[2] if len(lines) > 2 else ""

            # Remove repeated headers (e.g., "Title:" and "Experience:")
            title = title.replace("Title:", "").strip()
            experience = experience.replace("Experience:", "").strip()

            # Regular expression pattern to highlight number of years
            experience = re.sub(r"(\d+\+?)(\s*)(years|year)", r'**\1\2\3**', experience)

            # Display the information in separate lines
            st.write(f"**Job ID: {job_id_displayed}**")
            company_name = company.split(':')[-1].strip()  # Extract the company name
            st.write(f"**Company:** {company_name}")  # Make Company Name bold
            st.write(f"**Job Posting Link:** {url}")  # Make the job posting link bold
            st.write(f"**Job Title:** {title}")  # Make the job title bold

            years_of_experience = re.search(r"Years of Experience Required: (.+)", experience)
            if years_of_experience:
                years_of_experience = years_of_experience.group(1)
                st.write(f"**Years of Experience Required:** {years_of_experience}")
            else:
                st.write(f"**Experience:** {experience}")

            st.markdown("---")  # Add a separator between job postings

        # If fewer job postings were displayed than requested, inform the user
        if job_id_displayed < num_postings:
            st.warning(f"Only {job_id_displayed} out of {total_job_postings} job postings were available and displayed.")

            # experience = re.sub(pattern, r'**\1 \2**', experience)
            
            # job_id = i + 1
            # st.write(f"**Job ID: {job_id}**")
            # st.write(f"{company}")
            # st.write(f"Job Posting Link: {url}")
            # st.write(f"{title}")
            # st.write(f"{experience}")
            
            # if i < num_postings - 1:
            #     st.markdown("---") # Seperating each job from one another.
