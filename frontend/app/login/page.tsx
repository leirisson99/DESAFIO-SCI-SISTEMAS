import { loginBody, loginDisplay } from "./login-fonts"
import { LoginHero } from "./login-hero"

export default function LoginPage() {
  return (
    <div className={`${loginBody.variable} ${loginDisplay.variable}`}>
      <LoginHero />
    </div>
  )
}
