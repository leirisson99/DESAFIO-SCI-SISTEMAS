"use client"

import { useRouter } from "next/navigation"
import { useEffect, useRef, useState } from "react"

import styles from "@/app/login/login-hero.module.css"

const FALCON_SRC =
  "https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260813_052122_e77a27e6-17f1-4794-889b-3ceaa0e9e8cb.mp4"

const REF_W = 1464
const PANE_W = 628
const CARD_W = 613
const CARD_H = 922
const CONTENT_H = 580
const PHOTO_W_REF = 836
const IMG_W = 1352
const IMG_H = 1532
const IMG_REF_SCALE = PHOTO_W_REF / IMG_W
const PANE_RATIO = PANE_W / REF_W
const HERO_W = 681
const RAMP_HI = 1280
const RAMP_LO = 1000
const PHOTO_MIN = 0.42
const RAMP_LO2 = 820
const PHOTO_MIN2 = 0.36

function photoRatio(vw: number) {
  if (vw >= RAMP_HI) return 1 - PANE_RATIO
  if (vw <= RAMP_LO2) return PHOTO_MIN2
  if (vw <= RAMP_LO) {
    const t = (RAMP_LO - vw) / (RAMP_LO - RAMP_LO2)
    return PHOTO_MIN + (PHOTO_MIN2 - PHOTO_MIN) * t
  }
  const t = (RAMP_HI - vw) / (RAMP_HI - RAMP_LO)
  return 1 - PANE_RATIO + (PHOTO_MIN - (1 - PANE_RATIO)) * t
}

export function LoginHero() {
  const router = useRouter()
  const stageRef = useRef<HTMLDivElement>(null)
  const photoRef = useRef<HTMLDivElement>(null)
  const heroRef = useRef<HTMLDivElement>(null)
  const cardRef = useRef<HTMLDivElement>(null)
  const cardInRef = useRef<HTMLDivElement>(null)

  const badgeRef = useRef<HTMLDivElement>(null)
  const hl1Ref = useRef<HTMLSpanElement>(null)
  const hl2Ref = useRef<HTMLSpanElement>(null)
  const h1Ref = useRef<HTMLHeadingElement>(null)
  const subRef = useRef<HTMLParagraphElement>(null)
  const primaryRef = useRef<HTMLButtonElement>(null)

  const [entryPending, setEntryPending] = useState(true)

  useEffect(() => {
    const mqLandscape = window.matchMedia("(min-width: 700px) and (min-aspect-ratio: 51/50)")
    const mqPortrait = window.matchMedia("(min-width: 700px) and (max-aspect-ratio: 51/50)")

    function clearInline() {
      for (const el of [photoRef.current, heroRef.current, cardRef.current, cardInRef.current]) {
        if (el) el.style.cssText = ""
      }
    }

    function placeCard(paneW: number, vh: number) {
      const card = cardRef.current
      const cardIn = cardInRef.current
      if (!card || !cardIn) return
      const cs = Math.min(paneW / PANE_W, vh / CONTENT_H)
      const gapL = 1 * cs
      const mT = 14 * cs
      const mB = 13 * cs
      const mR = 14 * cs
      const cw = Math.max(CARD_W * cs, paneW - gapL - mR)
      const ch = vh - mT - mB
      card.style.left = gapL + "px"
      card.style.top = mT + "px"
      card.style.width = cw + "px"
      card.style.height = ch + "px"
      card.style.borderRadius = 26 * cs + "px"
      card.style.borderWidth = Math.max(1, cs) + "px"
      cardIn.style.transform = `translate(${(cw - CARD_W * cs) / 2}px,0) scale(${cs})`
    }

    function seatHero(photoW: number, vh: number) {
      const hero = heroRef.current
      if (!hero) return
      const imgScale = Math.max(photoW / IMG_W, vh / IMG_H)
      const s = Math.min(imgScale / IMG_REF_SCALE, (photoW * 0.92) / HERO_W)
      hero.style.transform = `scale(${s})`
    }

    function updateLayout() {
      const stage = stageRef.current
      const photo = photoRef.current
      const card = cardRef.current
      const cardIn = cardInRef.current
      if (!stage || !photo || !card || !cardIn) return

      clearInline()
      stage.classList.remove(styles.tabport, styles.stacked)

      const vw = window.innerWidth
      const vh = window.innerHeight

      if (mqLandscape.matches) {
        const ratio = photoRatio(vw)
        const photoW = vw * ratio
        photo.style.width = ratio * 100 + "%"
        placeCard(vw - photoW, vh)
        seatHero(photoW, vh)
      } else if (mqPortrait.matches) {
        stage.classList.add(styles.tabport)
        const band = Math.round(vh * 0.425)
        const sideM = Math.round(vw * 0.0525)
        stage.style.setProperty("--band-h", band + "px")
        stage.style.setProperty("--side-m", sideM + "px")
        const availH = vh - band - 40
        const paneW = vw - sideM * 2
        const cs = Math.min(paneW / PANE_W, availH / CONTENT_H)
        card.style.width = CARD_W * cs + "px"
        card.style.height = CARD_H * cs + "px"
        card.style.borderRadius = 26 * cs + "px"
        card.style.borderWidth = Math.max(1, cs) + "px"
        cardIn.style.transform = `scale(${cs})`
      } else {
        stage.classList.add(styles.stacked)
      }
    }

    updateLayout()
    window.addEventListener("resize", updateLayout, { passive: true })
    window.addEventListener("orientationchange", updateLayout)
    mqLandscape.addEventListener("change", updateLayout)
    mqPortrait.addEventListener("change", updateLayout)
    document.fonts?.ready.then(updateLayout).catch(() => {})

    return () => {
      window.removeEventListener("resize", updateLayout)
      window.removeEventListener("orientationchange", updateLayout)
      mqLandscape.removeEventListener("change", updateLayout)
      mqPortrait.removeEventListener("change", updateLayout)
    }
  }, [])

  useEffect(() => {
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches
    if (reduceMotion || typeof Element.prototype.animate !== "function") {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- one-time reveal based on a browser capability check, not a cascading state sync
      setEntryPending(false)
      return
    }

    let cancelled = false
    const ease = "cubic-bezier(.16,1,.3,1)"
    const softEase = "cubic-bezier(.22,1,.36,1)"
    const compact = window.matchMedia("(max-width: 699px)").matches
    const hlY = compact ? 12 : 16
    const cardY = compact ? 14 : 12

    async function run() {
      await Promise.race([
        document.fonts?.ready ?? Promise.resolve(),
        new Promise((resolve) => setTimeout(resolve, 650)),
      ])
      await new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))
      if (cancelled) return

      setEntryPending(false)

      const steps: Array<[Element | null, Keyframe[], number, number, string]> = [
        [cardRef.current, [{ opacity: 0, transform: `translateY(${cardY}px) scale(.988)` }, { opacity: 1, transform: "none" }], 40, 820, ease],
        [badgeRef.current, [{ opacity: 0, transform: "translateY(8px)" }, { opacity: 1, transform: "none" }], 120, 480, softEase],
        [hl1Ref.current, [{ opacity: 0, transform: `translateY(${hlY}px)`, clipPath: "inset(100% 0 0 0)" }, { opacity: 1, transform: "none", clipPath: "inset(0 0 0 0)" }], 240, 760, ease],
        [hl2Ref.current, [{ opacity: 0, transform: `translateY(${hlY}px)`, clipPath: "inset(100% 0 0 0)" }, { opacity: 1, transform: "none", clipPath: "inset(0 0 0 0)" }], 330, 760, ease],
        [h1Ref.current, [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }], 470, 620, ease],
        [subRef.current, [{ opacity: 0, transform: "translateY(10px)" }, { opacity: 1, transform: "none" }], 570, 560, ease],
        [primaryRef.current, [{ opacity: 0, transform: "translateY(8px)" }, { opacity: 1, transform: "none" }], 720, 560, ease],
      ]

      const animations = steps
        .filter(([el]) => el)
        .map(([el, kf, delay, duration, easing]) =>
          (el as Element).animate(kf, { delay, duration, easing, fill: "both" })
        )

      await Promise.allSettled(animations.map((a) => a.finished))
      if (!cancelled) {
        animations.forEach((a) => a.cancel())
      }
    }

    run()

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div
      ref={stageRef}
      className={`${styles.stage} ${entryPending ? styles.entryPending : ""}`}
    >
      <section ref={photoRef} className={styles.photo}>
        <video
          className={`${styles.photoImg} ${styles.photoImgTall}`}
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          src={FALCON_SRC}
        />
        <video
          className={`${styles.photoImg} ${styles.photoImgWide}`}
          aria-hidden="true"
          autoPlay
          muted
          loop
          playsInline
          preload="auto"
          src={FALCON_SRC}
        />
        <div className={styles.scrim} />
        <div ref={heroRef} className={styles.hero}>
          <div ref={badgeRef} className={styles.badge}>
            <svg className={styles.badgeGlyph} viewBox="0 0 582 557" aria-hidden="true">
              <path
                fillRule="evenodd"
                fill="#fff"
                d="M449.0 0.0 435.0 0.0 415.0 10.0 200.0 249.0 187.0 276.0 189.0 299.0 212.0 326.0 232.0 332.0 289.0 334.0 289.0 516.0 301.0 543.0 324.0 556.0 346.0 556.0 374.0 536.0 573.0 311.0 582.0 288.0 579.0 264.0 559.0 240.0 539.0 233.0 478.0 230.0 478.0 32.0 470.0 13.0ZM442.0 38.0 446.0 250.0 466.0 267.0 540.0 270.0 547.0 285.0 341.0 520.0 332.0 522.0 324.0 514.0 321.0 314.0 307.0 300.0 295.0 297.0 233.0 297.0 224.0 291.0 221.0 282.0ZM1.0 67.0 4.0 81.0 17.0 90.0 216.0 90.0 223.0 87.0 232.0 74.0 228.0 57.0 215.0 49.0 18.0 49.0 5.0 57.0ZM0.0 285.0 4.0 300.0 17.0 308.0 105.0 308.0 118.0 299.0 121.0 291.0 119.0 278.0 111.0 270.0 103.0 267.0 17.0 267.0 4.0 275.0ZM1.0 495.0 4.0 511.0 10.0 517.0 23.0 520.0 179.0 520.0 191.0 516.0 200.0 500.0 196.0 488.0 182.0 479.0 18.0 479.0 9.0 483.0Z"
              />
            </svg>
            <span id="badgeTxt">Atendimento com IA, sempre pronto</span>
          </div>
          <div className={styles.hlWrap}>
            <span ref={hl1Ref} className={`${styles.hl} ${styles.hl1} ${styles.displayFont}`}>
              Leve clareza
            </span>
            <span ref={hl2Ref} className={`${styles.hl} ${styles.hl2} ${styles.displayFont}`}>
              a cada conversa
            </span>
          </div>
        </div>
      </section>

      <section className={styles.pane}>
        <div ref={cardRef} className={styles.card}>
          <div ref={cardInRef} className={styles.cardIn}>
            <h1 ref={h1Ref} className={`${styles.col} ${styles.h1} ${styles.displayFont}`}>
              Bem-vindo!
            </h1>
            <p ref={subRef} className={`${styles.col} ${styles.sub}`}>
              Converse com nossa IA e tenha respostas claras na hora.
            </p>

            <button
              ref={primaryRef}
              type="button"
              className={styles.primaryBtn}
              onClick={() => router.push("/chat")}
            >
              <span>Vamos Começar</span>
            </button>
          </div>
        </div>
      </section>
    </div>
  )
}
