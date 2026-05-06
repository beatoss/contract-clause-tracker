def upload(client, filename, content):
    return client.post(
        "/api/documents",
        files={"file": (filename, content, "text/markdown")},
    )


def test_upload_markdown_imports_sentences_and_labels(client):
    content = """# Service Agreement

The total liability shall not exceed fees paid.

<!-- Clause Type: Limitation of Liability -->

The customer shall provide access.
"""
    response = upload(client, "service.md", content)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Service Agreement"
    assert [sentence["text"] for sentence in data["sentences"]] == [
        "The total liability shall not exceed fees paid.",
        "The customer shall provide access.",
    ]
    assert data["sentences"][0]["clause_type"] == "Limitation of Liability"
    assert data["sentences"][1]["clause_type"] is None


def test_update_and_clear_sentence_label(client):
    document = upload(client, "employment.md", "The employee agrees not to compete.").json()
    sentence_id = document["sentences"][0]["id"]

    update = client.patch(f"/api/sentences/{sentence_id}/label", json={"clause_type": "Non-Compete"})
    assert update.status_code == 200
    assert update.json()["clause_type"] == "Non-Compete"

    clear = client.patch(f"/api/sentences/{sentence_id}/label", json={"clause_type": None})
    assert clear.status_code == 200
    assert clear.json()["clause_type"] is None


def test_search_and_clause_filter(client):
    upload(
        client,
        "service.md",
        "The total liability shall not exceed fees paid.\n<!-- Clause Type: Limitation of Liability -->",
    )
    upload(client, "license.md", "The customer may terminate without cause.\n<!-- Clause Type: Termination for Convenience -->")

    search = client.get("/api/documents", params={"search": "license"})
    assert search.status_code == 200
    assert [document["filename"] for document in search.json()["documents"]] == ["license.md"]

    filtered = client.get("/api/documents", params={"clause_type": "Limitation of Liability"})
    assert filtered.status_code == 200
    assert [document["filename"] for document in filtered.json()["documents"]] == ["service.md"]


def test_group_by_clause_type(client):
    upload(client, "license.md", "The customer may terminate without cause.\n<!-- Clause Type: Termination for Convenience -->")

    response = client.get("/api/documents", params={"group_by": "clause_type"})

    assert response.status_code == 200
    groups = response.json()["groups"]
    assert groups[0]["group"] == "Termination for Convenience"
    assert groups[0]["documents"][0]["filename"] == "license.md"
