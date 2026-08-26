
SURVEYS = [
    {"title": "Mid-Year Check-in", "prompt": "How supported do you feel by your manager these past 6 months?", "department": "Marketing", "open_date": "2026-06-20", "close_date": "2026-07-20"},
    {"title": "Company Feedback", "prompt": "How satisfied are you with your opportunities for career growth thus far?", "department": "Finance", "open_date": "2026-08-10", "close_date": "2026-08-31"},
    {"title": "EOY Department Pulse", "prompt": "How would you describe our team culture and collaboration this past year?", "department": "Customer Service", "open_date": "2026-01-15", "close_date": "2026-02-15"},
    {"title": "Growth & Reflection", "prompt": "What is your primary professional focus or goal for next year and do you think these goals are supported by the company?", "department": "HR", "open_date": "2026-11-01", "close_date": "2026-12-31"},
    {"title": "Professional Development", "prompt": "What training or resources do you need to succeed for our next project and do you think the company is helpful in providing resources?", "department": "IT", "open_date": "2026-07-25", "close_date": "2026-10-25"}
]

RESPONSES = [
    # Negative sentiment
    {"response_text": "I feel as though my manager could listen more closely to my concerns. I recently had to take a leave of absence during a project and felt as though I was treated differently by my manager after returning."},
    # Positve sentiment, contains PII (name)
    {"response_text": "My manager, John Smith, has been super supportive in onboarding me! He listens to my concerns and is flexible when I feel like I need more time to gradually ramp up to the tasks we perform here."},
    # Positive sentiment
    {"response_text": "I'm impressed not only with what I've learned during my employment here but also the opportunities to take ownership of my work and to take on bigger responsibilities."},
    # Negative sentiment, contains PII (employment/employer history)
    {"response_text": "As someone with 5 years of experience in this field at Deloitte, I'm surprised by the lack of opportunities coming my way. It feels like I haven't been able to take on larger tasks even if I have the experience and expertise."},
    # Negative sentiment
    {"response_text": "This past year has definitely been busier than previous years, so I felt that I didn't get as many opportunities to interact and collaborate with the rest of the team. I believe this has been a detriment to our work performance and I can feel more tension at least between myself and others. I definitely think there are moments in time where we can continue to work on our team culture that we haven't been taking advantage of."},
    # Neutral sentiment, contains PII (email)
    {"response_text": "The team environment could be better. I tried emailing HR@company.com as well as our team lead jsmith@company.com to see if there were any opportunities for team building sessions, but received an inconclusive response. However, I've also been busier lately and having less other factors to worry about isn't the worst."},
    # Neutral sentiment
    {"response_text": "For the next year I intend to better familiarize myself with both the company policies and our team as a whole."},
    # Positive sentiment, contains PII (age/DOB)
    {"response_text": "I'm turning 30 next year (born 11/20/97)! I hope to work more on work-life balance and be able to spend more time with my son who is starting kindergarten! I think this company has done a good job in ensuring flexibility and providing benefits."},
    # Neutral sentiment
    {"response_text": "I think the team could use more professional training and resources in AWS. We've found ourselves stuck on things like permissions and server stores and I think it would be beneficial to have more training on how to handle, access, and navigate these areas of AWS. I think the company will find it beneficial, as it has in the past, to invest in these types of trainings."},
    # Positive sentiment, contains PII (name and phone number)
    {"response_text": "Our team is doing great, I can't of anything right now that we would need. Our newcomer, Billy has definitely filled in some of the gaps that we previously had and I feel confident we can get through this project just fine. The company has done a great job at stepping in whenever needed, however, so I'll be sure to be in touch if anything does come up! Can always give me a call: 123-456-7890"}
]