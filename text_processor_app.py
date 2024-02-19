import streamlit as st
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
from translate import Translator as TranslateLib

# Function to count words in text
def count_words(input_text):
    words = input_text.split()
    return len(words)

# Function to lemmatize text
def lemmatize_text(text):
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # Tokenize the text into sentences and words
    sentences = sent_tokenize(text)
    tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]

    # Lemmatize each word and remove stop words
    lemmatized_sentences = [
        [lemmatizer.lemmatize(word) for word in words if word.lower() not in stop_words]
        for words in tokenized_sentences
    ]

    return lemmatized_sentences

# Function to generate variable length summary
def variable_length_summary(text, summary_length_percentage=20):
    lemmatized_sentences = lemmatize_text(text)

    # Flatten the list of lemmatized words
    all_words = [word for sentence in lemmatized_sentences for word in sentence]

    # Calculate word frequency
    word_freq = Counter(all_words)

    # Calculate sentence importance based on word frequency
    sentence_importance = [sum(word_freq[word] for word in sentence) for sentence in lemmatized_sentences]

    # Calculate the total length of the summary in sentences
    num_sentences = int(len(lemmatized_sentences) * summary_length_percentage / 100)

    # Select sentences based on importance scores for summary
    summary_sentences = [lemmatized_sentences[i] for i in sorted(range(len(sentence_importance)),
                                                                 key=lambda k: sentence_importance[k], reverse=True)[:num_sentences]]

    # Join the summary sentences to form the final summary
    summary = ' '.join([' '.join(sentence) for sentence in summary_sentences])

    return summary

# Function to translate text with chunking
def translate_text_with_chunking(text, target_language='en', chunk_size=500):
    translator = TranslateLib(to_lang=target_language)

    # Break down the text into chunks
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Translate each chunk and concatenate the results
    translated_text = ""
    for chunk in chunks:
        translation = translator.translate(chunk)
        translated_text += translation

    return translated_text

# Streamlit UI
def main():
    st.title("Text Processor App")

    # Text Input
    input_text = st.text_area("Enter Text:", height=400)

    # Summary Length Percentage
    summary_length_percentage = st.slider("Summary Length Percentage:", 1, 100, 90)

    # Process Button
    if st.button("Summarize The Text "):
        try:
            # Variable length summary
            summary = variable_length_summary(input_text, summary_length_percentage)

            # Word count in the summary
            summary_word_count = count_words(summary)
            st.success(f"Number of words in the summary: {summary_word_count}")

            # Display the original summary
            st.subheader("Original Summary:")
            st.text_area("", summary, height=400)

            # Store the original summary in the app's state
            st.session_state.original_summary = summary

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

    # Translate Summary Button
    if st.button("Translate Summary"):
        try:
            # Translate summary
            target_language = st.selectbox("Target Language:", ['gu'])  # Hindi and for Gujarati('gu')
            original_summary = st.session_state.original_summary

            if original_summary:
                # Translate and display the translated summary
                translated_summary = translate_text_with_chunking(original_summary, target_language=target_language)
                st.subheader(f"Translated Summary in {target_language}:")
                st.text_area("", translated_summary, height=400)
            else:
                st.warning("Please process text first to generate a summary before translating.")

        except Exception as e:
            st.error(f"An error occurred during translation: {str(e)}")

if __name__ == "__main__":
    main()
