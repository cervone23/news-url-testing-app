"""
## App: URL AB Beta Testing App with Streamlit
Author: Brandon Cervone 
Source: [Github](https://github.com/)

Description:
This is built with Streamlit Framework and the Newspaper API.

Purpose:
Allow users to paste a URL address to find title, authors, and date published for any news publication. 

"""
# Core Pkgs
import streamlit as st 
import pandas as pd
from newspaper import Article

def main():
    """ URL Parse API APP with Streamlit """

    # Title
    st.title("AB URL Helper")
    st.subheader("Paste URL link below")

    ####################################################################
    ### User Input Fields ###
    ####################################################################

    # First Name Field 
    user_url = st.text_input("Paste URL Link Here:","")

    ####################################################################
    ### Extract URL Article Info ### 
    ####################################################################

    # Create a submission button to parse URL information 
    if st.button("Get URL Info"):
        url = str(user_url)
        article = Article(url)
        article.download()
        article.parse()

        url_title = article.title

        authors = article.authors
        url_authors = ''.join(map(str,authors))

        date = article.publish_date

        st.subheader("URL Title:")
        st.write(url_title) 
        st.subheader("URL Author(s):")
        st.write(url_authors)
        st.subheader("Date Published:")
        st.write(date.strftime('%m/%d/%Y'))

if __name__ == '__main__':
	main()
    