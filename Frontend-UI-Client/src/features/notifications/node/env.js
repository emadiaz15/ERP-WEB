// env.node.js (Node/Jest)
export function getIsDev() {
  return typeof process !== "undefined" && process.env && !!process.env.NODE_ENV && process.env.NODE_ENV === "development";
}
