import { Geist, Manrope } from "next/font/google"

export const loginBody = Geist({
  subsets: ["latin"],
  weight: ["400", "700"],
  variable: "--login-font-body",
})

export const loginDisplay = Manrope({
  subsets: ["latin"],
  weight: "variable",
  variable: "--login-font-display",
})
