class Discussion {
  constructor({ endpoint }) {
    this.endpoint = endpoint;
    this.threads = [];
  }

async loadThreads() {
    const response = await fetch(
      `${this.endpoint}/threads`
    );

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status}`
      );
    }

    this.threads = await response.json();

    return this.getThreads();
  }

  /**
   * Create a new discussion thread.
   */
  async createThread({ author, text }) {
    const thread = {
      id: crypto.randomUUID(),
      author,
      text,
      createdAt: new Date().toISOString(),
      replies: []
    };

    this.threads.push(thread);

    try {
      await this.#post("/threads", thread);
    } catch (err) {
      console.error("Failed to save thread", err);
    }

    return thread;
  }

  /**
   * Reply to an existing comment or thread.
   */
  async reply({ parentId, author, text }) {
    const parent = this.#findComment(parentId);

    if (!parent) {
      throw new Error(`Comment ${parentId} not found`);
    }

    const reply = {
      id: crypto.randomUUID(),
      parentId,
      author,
      text,
      createdAt: new Date().toISOString(),
      replies: []
    };

    parent.replies.push(reply);

    try {
      await this.#post(`/comments/${parentId}/replies`, reply);
    } catch (err) {
      console.error("Failed to save reply", err);
    }

    return reply;
  }

  /**
   * Get all discussion data.
   */
  getThreads() {
    return structuredClone(this.threads);
  }

  /**
   * Render as HTML.
   */
  render(container) {
    container.innerHTML = "";

    for (const thread of this.threads) {
      container.appendChild(this.#renderComment(thread));
    }
  }

  #renderComment(comment) {
    const el = document.createElement("div");
    el.className = "comment";

    el.innerHTML = `
      <div>
        <strong>${this.#escape(comment.author)}</strong>
        <small>${new Date(comment.createdAt).toLocaleString()}</small>
      </div>
      <div>${this.#escape(comment.text)}</div>
    `;

    const replies = document.createElement("div");
    replies.className = "replies";
    replies.style.marginLeft = "24px";

    for (const reply of comment.replies) {
      replies.appendChild(this.#renderComment(reply));
    }

    el.appendChild(replies);

    return el;
  }

  #findComment(id, comments = this.threads) {
    for (const comment of comments) {
      if (comment.id === id) {
        return comment;
      }

      const found = this.#findComment(id, comment.replies);

      if (found) {
        return found;
      }
    }

    return null;
  }

  async #post(path, payload) {
    console.info(JSON.stringify(payload))
    const response = await fetch(
      `${this.endpoint}${path}`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      }
    );

    if (!response.ok) {
      throw new Error(
        `HTTP ${response.status}`
      );
    }

    return response.json();
  }

  #escape(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}