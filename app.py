import streamlit as st

from research_rag.governance import normalize_role
from research_rag.models import ROLES
from research_rag.rag import RAGService

st.set_page_config(
    page_title="Research RAG Assistant",
    page_icon="🔎",
    layout="wide",
)

st.title("Research RAG Assistant")
st.caption(
    "Hybrid vector + keyword retrieval with document-level access controls."
)

with st.sidebar:
    user = st.text_input("User", value="demo-user")
    role = st.selectbox("Role", list(ROLES))
    st.caption("Try the same question with different roles.")

question = st.text_area(
    "Research question",
    placeholder="What is Alpha Fund's main liquidity risk?",
    height=100,
)

if st.button(
    "Ask",
    type="primary",
    disabled=not question.strip(),
):
    try:
        with st.spinner("Retrieving and generating..."):
            result = RAGService().answer(
                question.strip(),
                user.strip() or "anonymous",
                normalize_role(role),
            )

        st.subheader("Answer")
        st.markdown(result["answer"])
        st.caption(f"{result['elapsed_ms'] / 1000:.2f}s")

        st.subheader("Retrieved sources")
        for source, search_result in zip(
            result["sources"],
            result["results"],
        ):
            with st.expander(
                f"[{source['label']}] {source['title']} "
                f"— {source['classification']}"
            ):
                st.write(
                    {
                        "chunk": source["chunk"],
                        "hybrid_score": round(
                            search_result.score,
                            6,
                        ),
                        "vector_rank": search_result.vector_rank,
                        "keyword_rank": search_result.keyword_rank,
                    }
                )
                st.write(search_result.text)

                if source["source_url"]:
                    st.link_button(
                        "Open source",
                        source["source_url"],
                    )
    except Exception as error:
        st.error(str(error))
