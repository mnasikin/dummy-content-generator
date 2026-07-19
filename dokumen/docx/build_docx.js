// build_docx.js
// Dipanggil dari generate_dummy_docx.py via child_process.
// Usage: node build_docx.js <output_path> <num_paragraphs> <label> <site_mention> <mention_every_n>

const fs = require("fs");
const {
  Document,
  Packer,
  Paragraph,
  TextRun,
  HeadingLevel,
} = require("docx");

const [, , outputPath, numParagraphsArg, label, siteMention, mentionEveryNArg, textLengthArg] = process.argv;
const numParagraphs = parseInt(numParagraphsArg, 10);
const mentionEveryN = parseInt(mentionEveryNArg, 10);
const textLength = parseInt(textLengthArg || "200", 10);

function randomText(length = textLength) {
  const chars =
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ";
  let s = "";
  for (let i = 0; i < length; i++) {
    s += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return s;
}

const children = [
  new Paragraph({
    text: "Contoh File DOCX",
    heading: HeadingLevel.HEADING_1,
  }),
  new Paragraph({
    children: [new TextRun(`Ukuran: ${label}`)],
  }),
  new Paragraph({
    children: [new TextRun("Dummy file untuk testing development")],
  }),
  new Paragraph({ text: "" }),
];

for (let i = 1; i <= numParagraphs; i++) {
  const sumber = i % mentionEveryN === 0 ? siteMention : "-";
  children.push(
    new Paragraph({
      children: [
        new TextRun({
          text: `Paragraf ${i} - Dummy data testing - ${randomText()} (Sumber: ${sumber})`,
        }),
      ],
    })
  );
}

const doc = new Document({
  sections: [{ properties: {}, children }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.writeFileSync(outputPath, buffer);
});
