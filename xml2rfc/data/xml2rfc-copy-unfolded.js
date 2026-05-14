function stripSourcecodeMarkers(text) {
  const lines = text.split("\n");
  if (lines.length && /^<CODE BEGINS>(?: file "[^"]*")?$/.test(lines[0])) {
    lines.shift();
    if (lines.length && /^ file "[^"]*"$/.test(lines[0])) {
      lines.shift();
    }
  }
  if (lines.length && lines[lines.length - 1] === "<CODE ENDS>") {
    lines.pop();
  }
  return lines.join("\n");
}

function findHeader(lines) {
  const headers = [
    { strategy: "double", text: "NOTE: '\\\\' line wrapping per RFC 8792" },
    { strategy: "single", text: "NOTE: '\\' line wrapping per RFC 8792" },
  ];
  for (const header of headers) {
    if (lines[0].includes(header.text)) {
      return { strategy: header.strategy, index: 0 };
    }
    if (lines.length > 1 && lines[0].startsWith("<CODE BEGINS>") && lines[1].includes(header.text)) {
      return { strategy: header.strategy, index: 1 };
    }
    if (lines.length > 2 && lines[0].startsWith("<CODE BEGINS>") && lines[1].startsWith(" file \"") && lines[2].includes(header.text)) {
      return { strategy: header.strategy, index: 2 };
    }
  }
  return null;
}

function unfoldText(text, stripMarkers) {
  const lines = text.replace(/\r\n/g, "\n").replace(/\r/g, "\n").split("\n");
  const header = findHeader(lines);

  if (!header) {
    return text;
  }

  const before = lines.slice(0, header.index);
  if (lines[header.index].startsWith("<CODE BEGINS>")) {
    before.push("<CODE BEGINS>");
  }
  const after = lines.slice(header.index + 1);
  if (after.length && /^[ ]*$/.test(after[0])) {
    after.shift();
  }

  const folded = after.join("\n");
  const unwrapped = header.strategy === "double"
    ? folded.replace(/\\\n[ ]*\\/g, "")
    : folded.replace(/\\\n[ ]*/g, "");

  if (before.length) {
    const result = `${before.join("\n")}\n${unwrapped}`;
    return stripMarkers ? stripSourcecodeMarkers(result) : result;
  }
  return stripMarkers ? stripSourcecodeMarkers(unwrapped) : unwrapped;
}

function copyTextWithTextarea(text) {
  return new Promise((resolve, reject) => {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.top = "-1000px";
    textarea.style.left = "-1000px";
    document.body.appendChild(textarea);
    textarea.select();

    try {
      if (document.execCommand("copy")) {
        resolve();
      } else {
        reject(new Error("copy command failed"));
      }
    } catch (error) {
      reject(error);
    } finally {
      document.body.removeChild(textarea);
    }
  });
}

function copyText(text) {
  if (navigator.clipboard && navigator.clipboard.writeText) {
    return navigator.clipboard.writeText(text).catch(() => copyTextWithTextarea(text));
  }
  return copyTextWithTextarea(text);
}

document.querySelectorAll(".copy-unfolded").forEach(button => {
  button.addEventListener("click", () => {
    const block = button.closest(".has-copy-unfolded");
    const pre = block ? block.querySelector("pre") : null;
    if (!block || !pre) {
      return;
    }

    const text = unfoldText(pre.textContent, block.dataset.sourcecodeMarkers === "true");
    copyText(text).then(() => {
      button.textContent = "Copied";
      button.setAttribute("aria-label", "Copied");
      window.setTimeout(() => {
        button.textContent = "Copy unfolded";
        button.setAttribute("aria-label", "Copy unfolded");
      }, 1600);
    }).catch(() => {
      button.textContent = "Error";
      window.setTimeout(() => {
        button.textContent = "Copy unfolded";
      }, 1600);
    });
  });
});
