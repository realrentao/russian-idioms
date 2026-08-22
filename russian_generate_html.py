# -*- coding: utf-8 -*-
"""
Russian Idioms Interactive HTML Generator
Generates index.html navigation page + individual idiom pages
With edge-tts audio (ru-RU-SvetlanaNeural) + three-speed playback

Adapted from the Italian Idioms generator (realrentao/italian-idioms).
Key adaptations: Russian voice, Russian flag (white-blue-red), Russian palette,
Russian category map, Cyrillic-aware fill grading.
"""

import json
import os
import base64
import hashlib
import sys
import re
import asyncio
import edge_tts

# Ensure UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Import data
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from russian_idioms_data import IDIOMS

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
VOICE = "ru-RU-SvetlanaNeural"   # Russian female voice

# ==================== CSS STYLES ====================

COMMON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&family=Noto+Serif+SC:wght@400;600;700&display=swap');

/* === Russian Idioms - Global Styles === */

:root {
    --ita-green: #0039A6;   /* repurposed: Russian blue */
    --ita-white: #F5F5F0;
    --ita-red: #D52B1E;     /* Russian red */
    --gold: #C4A35A;
    --gold-light: #F0E6C8;
    --gold-dark: #A0813A;
    --cream: #FDF8F0;
    --warm-bg: #FAF6EE;
    --card-bg: #FFFFFF;
    --text-dark: #2C2416;
    --text-mid: #6B5D4A;
    --text-light: #9A8B75;
    --shadow: 0 4px 20px rgba(0,0,0,0.08);
    --shadow-hover: 0 8px 32px rgba(0,0,0,0.12);
    --radius: 16px;
    --radius-sm: 8px;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
    font-family: 'Inter', sans-serif;
    background: var(--warm-bg);
    color: var(--text-dark);
    line-height: 1.7;
    min-height: 100vh;
}

/* Tricolor Header (Russian: blue-white-red) */
.tricolor-bar {
    height: 4px;
    background: linear-gradient(90deg, var(--ita-green) 0%, var(--ita-green) 33.33%, var(--ita-white) 33.33%, var(--ita-white) 66.66%, var(--ita-red) 66.66%, var(--ita-red) 100%);
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 1000;
    box-shadow: 0 1px 2px rgba(0,0,0,0.15);
}

.main-header {
    background: linear-gradient(135deg, #2C2416 0%, #4A3828 100%);
    padding: 60px 20px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(196,163,90,0.08) 0%, transparent 50%),
                radial-gradient(circle at 70% 50%, rgba(213,43,30,0.05) 0%, transparent 50%);
    pointer-events: none;
}

.main-header h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    color: var(--gold);
    font-weight: 700;
    letter-spacing: 2px;
    margin-bottom: 8px;
    position: relative;
}

.main-header .subtitle {
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 1.2rem;
    color: var(--gold-light);
    opacity: 0.8;
    position: relative;
}

.main-header .subtitle-cn {
    font-family: 'Noto Serif SC', serif;
    font-size: 1rem;
    color: var(--text-light);
    margin-top: 6px;
    position: relative;
}

/* Footer */
.page-footer {
    background: linear-gradient(135deg, #2C2416 0%, #4A3828 100%);
    color: var(--text-light);
    text-align: center;
    padding: 24px 20px;
    font-size: 0.85rem;
}

/* Back to Top */
.back-to-top {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: var(--gold);
    color: white;
    border: none;
    cursor: pointer;
    font-size: 1.4rem;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    opacity: 0;
    pointer-events: none;
    z-index: 999;
}

.back-to-top.visible {
    opacity: 1;
    pointer-events: auto;
}

.back-to-top:hover {
    background: var(--gold-dark);
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
}

/* Inline Play Button */
.inline-play-btn {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    border: 1px solid var(--gold-light);
    background: white;
    color: var(--gold-dark);
    font-size: 0.7rem;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 4px;
    padding: 0;
    line-height: 1;
    vertical-align: middle;
}

/* Translation Toggle Button */
.trans-btn {
    width: 24px;
    height: 24px;
    border-radius: 4px;
    border: 1px solid var(--ita-green);
    background: white;
    color: var(--ita-green);
    font-size: 0.65rem;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-left: 4px;
    padding: 0;
    line-height: 1;
}

.trans-btn:hover {
    background: var(--ita-green);
    color: white;
}

.trans-btn.active {
    background: var(--ita-green);
    color: white;
}

/* Translation Text (hidden by default) */
.trans-text {
    display: none;
    font-size: 0.85rem;
    color: var(--ita-green);
    font-weight: 500;
    padding: 6px 12px;
    margin: 6px 0 2px 0;
    background: rgba(0,57,166,0.05);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--ita-green);
    line-height: 1.5;
    width: 100%;
    font-family: 'Noto Serif SC', serif;
}

.trans-text.visible {
    display: block;
}

/* Align trans-text with the value text (after label), not the label itself */
.meaning-item .trans-text {
    margin-left: 78px;
    width: calc(100% - 78px);
}
.meaning-item .trans-text.visible {
    display: block;
}

.example-line .trans-text {
    margin-left: 30px;
    width: calc(100% - 30px);
}
.example-line .trans-text.visible {
    display: block;
}

.inline-play-btn:hover {
    background: var(--gold);
    color: white;
    border-color: var(--gold);
    transform: scale(1.1);
}

.inline-play-btn.playing {
    background: var(--ita-red);
    color: white;
    border-color: var(--ita-red);
    animation: inlinePulse 0.8s infinite;
}

@keyframes inlinePulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(213,43,30,0.3); }
    50% { box-shadow: 0 0 0 6px rgba(213,43,30,0); }
}

/* Speed Labels */
.speed-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ============ CSS Flags (emoji-free) ============ */
.flag-icon {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    vertical-align: middle;
}

.flag-icon svg {
    width: 1em;
    height: 1em;
    border-radius: 2px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.15);
    flex-shrink: 0;
}

.flag-it svg { width: 1em; height: 1em; }
.flag-cn svg { width: 1em; height: 1em; }
.flag-en svg { width: 1em; height: 1em; }
.flag-ru svg { width: 1em; height: 1em; }

.flag-it .label,
.flag-cn .label,
.flag-en .label,
.flag-ru .label {
    font-size: 0.85rem;
    font-weight: 500;
}

@media (max-width: 768px) {
    .main-header h1 { font-size: 2rem; }
    .main-header .subtitle { font-size: 1rem; }
    .main-header { padding: 50px 16px 30px; }
}

@media (max-width: 480px) {
    .main-header h1 { font-size: 1.6rem; }
}
"""

INDEX_CSS = """
/* === Index Page Specific Styles === */
.search-bar {
    max-width: 500px;
    margin: -24px auto 40px;
    padding: 0 20px;
    position: relative;
    z-index: 10;
}

.search-bar input {
    width: 100%;
    padding: 14px 20px 14px 48px;
    border: 2px solid var(--gold-light);
    border-radius: 50px;
    font-size: 1rem;
    background: var(--card-bg);
    color: var(--text-dark);
    outline: none;
    transition: all 0.3s ease;
    box-shadow: var(--shadow);
}

.search-bar input:focus {
    border-color: var(--gold);
    box-shadow: var(--shadow-hover);
}

.search-bar .search-icon {
    position: absolute;
    left: 36px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-light);
    font-size: 1.1rem;
}

.idiom-grid {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px 60px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
    gap: 20px;
}

.idiom-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow);
    transition: all 0.3s ease;
    cursor: pointer;
    text-decoration: none;
    display: block;
    position: relative;
    overflow: hidden;
    border: 1px solid transparent;
}

.idiom-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--ita-green), var(--gold), var(--ita-red));
    opacity: 0;
    transition: opacity 0.3s ease;
}

.idiom-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-hover);
    border-color: var(--gold-light);
}

.idiom-card:hover::before {
    opacity: 1;
}

.idiom-card .card-number {
    font-family: 'Playfair Display', serif;
    font-size: 0.8rem;
    color: var(--gold);
    font-weight: 600;
    margin-bottom: 4px;
    letter-spacing: 1px;
}

.idiom-card .card-idiom {
    font-family: 'Playfair Display', serif;
    font-size: 1.15rem;
    color: var(--text-dark);
    font-weight: 600;
    margin-bottom: 6px;
    line-height: 1.4;
}

.idiom-card .card-category {
    font-size: 0.75rem;
    color: var(--ita-red);
    font-weight: 500;
    margin-bottom: 8px;
    letter-spacing: 0.5px;
}

.idiom-card .card-meaning {
    font-family: 'Noto Serif SC', serif;
    font-size: 0.9rem;
    color: var(--text-mid);
    line-height: 1.5;
}

.idiom-card .card-hint {
    font-size: 0.8rem;
    color: var(--gold-dark);
    margin-top: 10px;
    font-style: italic;
}

/* No results */
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-light);
    font-size: 1.1rem;
    display: none;
}

/* Stats bar */
.stats-bar {
    max-width: 1200px;
    margin: 0 auto 20px;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
}

.stats-bar .count {
    font-size: 0.9rem;
    color: var(--text-mid);
}

.stats-bar .count strong {
    color: var(--text-dark);
    font-weight: 600;
}

.category-filters {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

.category-tag {
    padding: 4px 14px;
    border-radius: 50px;
    font-size: 0.75rem;
    font-weight: 500;
    background: var(--card-bg);
    border: 1px solid var(--gold-light);
    color: var(--text-mid);
    cursor: pointer;
    transition: all 0.2s ease;
}

.category-tag:hover,
.category-tag.active {
    background: var(--gold);
    color: white;
    border-color: var(--gold);
}

@media (max-width: 768px) {
    .idiom-grid {
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 14px;
        padding: 0 14px 40px;
    }
    .stats-bar { flex-direction: column; align-items: flex-start; }
}

@media (max-width: 480px) {
    .idiom-grid {
        grid-template-columns: 1fr;
    }
}
"""

IDIOM_PAGE_CSS = """
/* === Idiom Detail Page Styles === */
.idiom-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 30px 20px 60px;
}

/* Breadcrumb */
.breadcrumb {
    font-size: 0.85rem;
    color: var(--text-mid);
    margin-bottom: 20px;
    padding: 0 20px;
    max-width: 800px;
    margin-left: auto;
    margin-right: auto;
}

.breadcrumb a {
    color: var(--gold-dark);
    text-decoration: none;
    transition: color 0.2s;
}

.breadcrumb a:hover {
    color: var(--gold);
}

/* Hero Section */
.idiom-hero {
    background: linear-gradient(135deg, #2C2416 0%, #4A3828 100%);
    border-radius: var(--radius);
    padding: 40px;
    text-align: center;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}

.idiom-hero::before {
    content: '"';
    position: absolute;
    top: -20px;
    left: 20px;
    font-family: 'Playfair Display', serif;
    font-size: 12rem;
    color: rgba(196,163,90,0.08);
    line-height: 1;
}

.idiom-hero::after {
    content: '"';
    position: absolute;
    bottom: -80px;
    right: 20px;
    font-family: 'Playfair Display', serif;
    font-size: 12rem;
    color: rgba(196,163,90,0.08);
    line-height: 1;
}

.idiom-hero .idiom-number {
    font-family: 'Playfair Display', serif;
    font-size: 0.9rem;
    color: var(--gold);
    letter-spacing: 2px;
    margin-bottom: 8px;
    position: relative;
    z-index: 1;
}

.idiom-hero .idiom-text {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: white;
    font-weight: 700;
    line-height: 1.3;
    margin-bottom: 10px;
    position: relative;
    z-index: 1;
}

.idiom-hero .idiom-meaning-cn {
    font-family: 'Noto Serif SC', serif;
    font-size: 1.1rem;
    color: var(--gold-light);
    position: relative;
    z-index: 1;
}

.idiom-hero .idiom-english {
    font-style: italic;
    font-size: 0.85rem;
    color: rgba(255,255,255,0.5);
    margin-top: 6px;
    position: relative;
    z-index: 1;
}

/* Audio Player */
.audio-player {
    display: flex;
    align-items: center;
    gap: 12px;
    justify-content: center;
    margin-top: 20px;
    position: relative;
    z-index: 1;
    flex-wrap: wrap;
}

.audio-btn {
    width: 52px;
    height: 52px;
    border-radius: 50%;
    border: none;
    background: rgba(255,255,255,0.15);
    color: white;
    font-size: 1.3rem;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    backdrop-filter: blur(4px);
}

.audio-btn:hover {
    background: var(--gold);
    transform: scale(1.05);
}

.audio-btn.playing {
    background: var(--ita-red);
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(213,43,30,0.4); }
    50% { box-shadow: 0 0 0 12px rgba(213,43,30,0); }
}

.speed-buttons {
    display: flex;
    gap: 6px;
}

.speed-btn {
    padding: 6px 14px;
    border: 1px solid rgba(255,255,255,0.25);
    border-radius: 20px;
    background: transparent;
    color: rgba(255,255,255,0.7);
    font-size: 0.78rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
}

.speed-btn:hover {
    background: rgba(255,255,255,0.15);
    color: white;
}

.speed-btn.active {
    background: var(--gold);
    color: white;
    border-color: var(--gold);
}

/* Content Cards */
.section-card {
    background: var(--card-bg);
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    margin-bottom: 20px;
    overflow: hidden;
    border: 1px solid rgba(196,163,90,0.15);
}

.section-header {
    padding: 18px 24px;
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 1.1rem;
    border-bottom: 1px solid var(--gold-light);
    display: flex;
    align-items: center;
    gap: 10px;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
}

.section-header:hover {
    background: rgba(196,163,90,0.05);
}

.section-header .icon {
    font-size: 1.2rem;
}

.section-header .toggle-arrow {
    margin-left: auto;
    transition: transform 0.3s ease;
    font-size: 0.9rem;
    color: var(--text-light);
}

.section-header.collapsed .toggle-arrow {
    transform: rotate(-90deg);
}

.section-body {
    padding: 24px;
    transition: all 0.3s ease;
}

.section-body.collapsed {
    display: none;
}

/* Meaning Section */
.meaning-item {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 10px 0;
    border-bottom: 1px solid rgba(196,163,90,0.1);
}

.meaning-item:last-child {
    border-bottom: none;
}

.meaning-item .label {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--gold-dark);
    min-width: 70px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.meaning-item .value {
    font-size: 0.95rem;
    color: var(--text-dark);
    line-height: 1.6;
    flex: 1;
}

.meaning-item .value.cn {
    font-family: 'Noto Serif SC', serif;
}

/* Examples */
.example-group {
    background: var(--cream);
    border-radius: var(--radius-sm);
    padding: 16px 20px;
    margin-bottom: 12px;
}

.example-line {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    padding: 4px 0;
    font-size: 0.92rem;
    line-height: 1.6;
}

.example-line .speaker {
    font-weight: 600;
    color: var(--ita-green);
    min-width: 24px;
}

.example-line .speaker-b {
    color: var(--ita-red);
}

.example-line .text {
    color: var(--text-dark);
    flex: 1;
}

/* Cultural Note */
.cultural-note {
    background: linear-gradient(135deg, var(--cream) 0%, #FFF 100%);
    border-left: 3px solid var(--gold);
    padding: 16px 20px;
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    font-size: 0.92rem;
    line-height: 1.7;
    color: var(--text-mid);
}

/* Exercises */
.exercise-item {
    padding: 16px 0;
    border-bottom: 1px solid rgba(196,163,90,0.1);
}

.exercise-item:last-child {
    border-bottom: none;
}

.exercise-q {
    font-weight: 500;
    margin-bottom: 10px;
    font-size: 0.92rem;
}

.exercise-options {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 10px;
}

.exercise-opt {
    padding: 8px 14px;
    border: 1px solid var(--gold-light);
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.88rem;
    background: white;
}

.exercise-opt:hover {
    border-color: var(--gold);
    background: var(--cream);
}

.exercise-opt.selected {
    border-color: var(--ita-green);
    background: rgba(0,57,166,0.08);
    font-weight: 500;
}

.exercise-opt.wrong {
    border-color: var(--ita-red);
    background: rgba(213,43,30,0.08);
}

.exercise-opt.correct {
    border-color: var(--ita-green);
    background: rgba(0,57,166,0.12);
}

.exercise-answer {
    font-size: 0.85rem;
    color: var(--ita-green);
    font-weight: 500;
    margin-top: 6px;
    display: none;
}

.exercise-answer.show {
    display: block;
}

.exercise-blank {
    font-size: 0.9rem;
    color: var(--text-dark);
    margin: 8px 0;
    padding: 10px 14px;
    background: var(--cream);
    border-radius: var(--radius-sm);
    border: 1px dashed var(--gold-light);
}

.exercise-blank .fill-word {
    color: var(--ita-red);
    font-weight: 600;
    cursor: pointer;
    border-bottom: 2px dotted var(--ita-red);
}

.exercise-blank .fill-answer {
    color: var(--ita-green);
    font-weight: 600;
}

.reveal-btn {
    padding: 8px 20px;
    border: 1px solid var(--gold);
    border-radius: 20px;
    background: white;
    color: var(--gold-dark);
    font-size: 0.85rem;
    cursor: pointer;
    transition: all 0.2s ease;
    margin-top: 6px;
}

.reveal-btn:hover {
    background: var(--gold);
    color: white;
}

/* === Fill-in Typing Exercise === */
.fill-exercise {
    margin: 12px 0;
}

.fill-input-row {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
}

.fill-input {
    flex: 1;
    min-width: 180px;
    padding: 10px 14px;
    border: 2px solid var(--gold-light);
    border-radius: var(--radius-sm);
    font-size: 0.95rem;
    background: white;
    color: var(--text-dark);
    outline: none;
    transition: all 0.2s ease;
    font-family: 'Inter', sans-serif;
}

.fill-input:focus {
    border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(196,163,90,0.15);
}

.fill-input.correct {
    border-color: var(--ita-green);
    background: rgba(0,57,166,0.05);
}

.fill-input.wrong {
    border-color: var(--ita-red);
    background: rgba(213,43,30,0.05);
}

.fill-check-btn {
    padding: 10px 20px;
    border: none;
    border-radius: var(--radius-sm);
    background: var(--ita-green);
    color: white;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    white-space: nowrap;
}

.fill-check-btn:hover {
    background: #002a78;
    transform: translateY(-1px);
}

.fill-feedback {
    font-size: 0.85rem;
    margin-top: 6px;
    font-weight: 500;
    padding: 4px 0;
}

.fill-feedback.correct {
    color: var(--ita-green);
}

.fill-feedback.wrong {
    color: var(--ita-red);
}

.fill-feedback.hint {
    color: var(--gold-dark);
}

.fill-answer {
    font-size: 0.88rem;
    color: var(--ita-green);
    font-weight: 600;
    margin-top: 8px;
    padding: 8px 14px;
    background: rgba(0,57,166,0.06);
    border-radius: var(--radius-sm);
    border: 1px solid rgba(0,57,166,0.2);
    display: none;
}

/* Navigation between idioms */
.nav-idioms {
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    gap: 12px;
    margin: 28px auto;
    max-width: 800px;
    padding: 0 20px;
}

.nav-idioms .nav-btn.prev { justify-self: start; }
.nav-idioms .nav-btn.next { justify-self: end; }
.nav-idioms .nav-home { justify-self: center; }

.nav-btn {
    padding: 12px 24px;
    border: 1px solid var(--gold-light);
    border-radius: 50px;
    text-decoration: none;
    color: var(--text-dark);
    font-size: 0.88rem;
    font-weight: 500;
    transition: all 0.3s ease;
    background: var(--card-bg);
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.nav-btn:hover {
    border-color: var(--gold);
    background: var(--cream);
    transform: translateY(-1px);
}

.nav-btn.next {
    margin-left: auto;
}

.nav-btn.disabled {
    opacity: 0.3;
    pointer-events: none;
}

@media (max-width: 768px) {
    .idiom-hero { padding: 30px 20px; }
    .idiom-hero .idiom-text { font-size: 1.5rem; }
    .section-header { padding: 14px 18px; font-size: 1rem; }
    .section-body { padding: 18px; }
    .nav-idioms { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; }
    .nav-idioms .nav-btn.prev { justify-self: auto; }
    .nav-idioms .nav-btn.next { justify-self: auto; }
    .nav-idioms .nav-home { justify-self: auto; }
}

@media (max-width: 480px) {
    .idiom-hero { padding: 24px 16px; }
    .idiom-hero .idiom-text { font-size: 1.25rem; }
    .audio-player { gap: 8px; }
    .idiom-container { padding: 20px 12px 40px; }
}
"""

# ==================== SVG FLAGS ====================

def svg_flag_ru():
    """Russian flag SVG (white-blue-red horizontal tricolor)"""
    return '<svg width="1em" height="1em" viewBox="0 0 3 2" xmlns="http://www.w3.org/2000/svg"><rect width="3" height="2" fill="#FFFFFF"/><rect y="0.666" width="3" height="0.667" fill="#0039A6"/><rect y="1.333" width="3" height="0.667" fill="#D52B1E"/></svg>'

def svg_flag_cn():
    """Chinese flag SVG (red with 5 yellow stars)"""
    return '<svg width="1em" height="1em" viewBox="0 0 30 20" xmlns="http://www.w3.org/2000/svg"><rect width="30" height="20" fill="#DE2910"/><polygon points="5.2,2.8 5.8,4.5 7.6,4.5 6.1,5.7 6.7,7.4 5.2,6.2 3.7,7.4 4.3,5.7 2.8,4.5 4.6,4.5" fill="#FFDE00"/><polygon points="12,3.6 12.3,4.5 13.2,4.5 12.5,5.1 12.8,6 12,5.4 11.2,6 11.5,5.1 10.8,4.5 11.7,4.5" fill="#FFDE00"/><polygon points="13.8,7.4 14.3,8.1 15.1,8 14.6,8.6 15,9.4 14.2,9.2 13.6,9.8 13.6,9 12.8,8.7 13.6,8.4" fill="#FFDE00"/><polygon points="12,10.8 12.5,11.5 13.3,11.3 12.8,12 13.2,12.8 12.4,12.5 11.8,13.1 11.8,12.3 11,12.1 11.8,11.8" fill="#FFDE00"/><polygon points="9.2,10.2 9.5,11 10.4,11 9.7,11.5 10,12.4 9.2,11.9 8.4,12.3 8.7,11.4 8,10.9 8.9,10.8" fill="#FFDE00"/></svg>'

def svg_flag_en():
    """UK flag SVG (Union Jack simplified)"""
    return '<svg width="1em" height="1em" viewBox="0 0 60 30" xmlns="http://www.w3.org/2000/svg"><clipPath id="s"><path d="M0,0 v30 h60 v-30 z"/></clipPath><clipPath id="t"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath><g clip-path="url(#s)"><path d="M0,0 v30 h60 v-30 z" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#FFF" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#C8102E" stroke-width="2"/><path d="M30,0 v30 M0,15 h60" stroke="#FFF" stroke-width="10"/><path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="4"/></g></svg>'


# ==================== GENERATOR FUNCTIONS ====================

def safe_filename(key):
    """Create a URL-safe base64 filename from a string key"""
    key_bytes = key.encode('utf-8')
    return base64.urlsafe_b64encode(key_bytes).decode('ascii').rstrip('=')

def slugify(text):
    """Convert text to URL-friendly slug"""
    s = text.lower().strip()
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[\s_]+', '-', s)
    s = re.sub(r'-+', '-', s)
    return s[:50]

def generate_categories():
    """Get unique categories from idioms"""
    cats = set()
    for idiom in IDIOMS:
        for c in idiom["category"].split(" / "):
            cats.add(c.strip())
    return sorted(cats)

# Category Chinese translations (Russian categories)
CATEGORY_CN = {
    "Человек": "人性",
    "Речь и поведение": "言行",
    "Труд и лень": "勤劳与懒惰",
    "Дружба и отношения": "友谊与关系",
    "Мудрость": "智慧",
    "Судьба": "命运",
    "Осторожность": "谨慎",
    "Характер": "性格",
    "Правда и ложь": "真伪",
    "Семья": "家庭",
    "Количество": "数量",
    "Качество": "品质",
    "Время и судьба": "时间与命运",
    "Чувства": "情感",
}

def get_inline_texts(idiom):
    """Get all Russian texts that need inline audio for an idiom"""
    texts = {}
    texts['meaning'] = idiom['meaning_it']
    examples = []
    for pair in idiom['examples']:
        examples.append(pair[1])  # Russian text
    texts['examples'] = examples
    return texts

def text_hash(text):
    """Create short hash for a text string"""
    return hashlib.md5(text.encode('utf-8')).hexdigest()[:12]

# ---------- edge-tts audio generation (async, concurrent) ----------
async def _speak(text, out_path, sem):
    async with sem:
        try:
            comm = edge_tts.Communicate(text, VOICE)
            await comm.save(out_path)
        except Exception as e:
            print(f"    ✗ {e}")

async def _run_batch(jobs, label):
    sem = asyncio.Semaphore(12)
    await asyncio.gather(*[_speak(t, p, sem) for t, p in jobs])
    print(f"  {label}: {len(jobs)} generated")

def generate_audio_files():
    """Generate main idiom audio (skips existing) via edge-tts module"""
    os.makedirs(AUDIO_DIR, exist_ok=True)
    jobs = []
    for idiom in IDIOMS:
        text = idiom['idiom']
        base = safe_filename(text)
        ap = os.path.join(AUDIO_DIR, f"{base}.mp3")
        if os.path.exists(ap) and os.path.getsize(ap) > 1000:
            continue
        jobs.append((text, ap))
    if jobs:
        asyncio.run(_run_batch(jobs, "main audio"))
    print(f"  ✓ main audio files ready (skipped existing)")

def generate_inline_audio_files():
    """Generate edge-tts audio for meaning and example texts, return dict of hash->base64"""
    os.makedirs(AUDIO_DIR, exist_ok=True)

    all_texts = {}
    for idiom in IDIOMS:
        texts = get_inline_texts(idiom)
        all_texts[text_hash(texts['meaning'])] = texts['meaning']
        for ex in texts['examples']:
            all_texts[text_hash(ex)] = ex

    jobs = []
    for h, text in all_texts.items():
        fp = os.path.join(AUDIO_DIR, f"inline_{h}.mp3")
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            continue
        jobs.append((text, fp))

    if jobs:
        asyncio.run(_run_batch(jobs, "inline audio"))

    audio_cache = {}
    for h, text in all_texts.items():
        fp = os.path.join(AUDIO_DIR, f"inline_{h}.mp3")
        if os.path.exists(fp) and os.path.getsize(fp) > 1000:
            with open(fp, 'rb') as f:
                audio_cache[h] = base64.b64encode(f.read()).decode('ascii')
    print(f"  ✓ inline cache: {len(audio_cache)} clips")
    return audio_cache

def build_inline_audio_json(audio_cache):
    """Build individual JSON files for each audio clip"""
    DATA_DIR = os.path.join(OUTPUT_DIR, "data")
    os.makedirs(DATA_DIR, exist_ok=True)

    print(f"\nBuilding individual audio JSON files...")

    total = 0
    for idiom in IDIOMS:
        iid = idiom['id']
        texts = get_inline_texts(idiom)

        meaning_b64 = audio_cache.get(text_hash(texts['meaning']), '')
        if meaning_b64:
            fname = f"idiom-{iid:02d}-audio-meaning.json"
            fpath = os.path.join(DATA_DIR, fname)
            with open(fpath, 'w', encoding='utf-8') as f:
                json.dump(meaning_b64, f)
            total += 1

        for ei, ex_b64 in enumerate([audio_cache.get(text_hash(ex), '') for ex in texts['examples']]):
            if ex_b64:
                fname = f"idiom-{iid:02d}-audio-ex-{ei}.json"
                fpath = os.path.join(DATA_DIR, fname)
                with open(fpath, 'w', encoding='utf-8') as f:
                    json.dump(ex_b64, f)
                total += 1

    print(f"  Generated {total} individual audio JSON files")
    print(f"  Total: {total} files in data/")


def generate_index_html():
    """Generate the main navigation page"""
    categories = generate_categories()

    cards_html = ""
    for idiom in IDIOMS:
        cats = idiom["category"].split(" / ")
        cat_classes = " ".join([slugify(c) for c in cats])
        cards_html += f"""
        <a href="idiom-{idiom['id']:02d}.html" class="idiom-card" data-category="{cat_classes}" data-search="{idiom['idiom'].lower()} {idiom['meaning_cn']}">
            <div class="card-number">#{idiom['id']:02d}</div>
            <div class="card-idiom">{idiom['idiom']}</div>
            <div class="card-category">{idiom['category']}</div>
            <div class="card-meaning">{idiom['meaning_cn']}</div>
            <div class="card-hint">{idiom['english_eq']}</div>
        </a>
        """

    cat_filters = ""
    for c in categories:
        c_cn = CATEGORY_CN.get(c, '')
        display = f"{c} {c_cn}" if c_cn else c
        cat_filters += f'<span class="category-tag" data-cat="{slugify(c)}" onclick="filterByCategory(\'{slugify(c)}\', this)">{display}</span>\n                '

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>俄语习语 | 涛子办事处</title>
<style>
{COMMON_CSS}
{INDEX_CSS}
</style>
</head>
<body>

<div class="tricolor-bar"></div>

<header class="main-header">
    <h1><span class="flag-icon flag-ru">{svg_flag_ru()}</span> 俄语习语</h1>
    <div class="subtitle">Русские фразеологизмы и поговорки</div>
    <div class="subtitle-cn">常用俄语习语，轻松掌握地道表达</div>
</header>

<div class="search-bar">
    <span class="search-icon">🔍</span>
    <input type="text" id="searchInput" placeholder="搜索习语 / Найти фразеологизм..." oninput="filterIdioms()">
</div>

<div class="stats-bar">
    <div class="count">共 <strong>{len(IDIOMS)}</strong> 个习语</div>
    <div class="category-filters">
        <span class="category-tag active" data-cat="all" onclick="filterByCategory('all', this)">全部</span>
        {cat_filters}
    </div>
</div>

<div class="idiom-grid" id="idiomGrid">
    {cards_html}
</div>

<div class="no-results" id="noResults">
    没有找到匹配的习语 😅
</div>

<footer class="page-footer">
    <p>涛子办事处 &bull; 俄语习语学习工具</p>
</footer>

<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
// Search & Filter
function filterIdioms() {{
    const q = document.getElementById('searchInput').value.toLowerCase().trim();
    const cards = document.querySelectorAll('.idiom-card');
    const activeCat = document.querySelector('.category-tag.active:not([data-cat="all"])');
    let visible = false;

    cards.forEach(c => {{
        const searchText = c.dataset.search;
        const cats = c.dataset.category.split(' ');
        const matchSearch = !q || searchText.includes(q);
        const matchCat = !activeCat || cats.includes(activeCat.dataset.cat);

        if (matchSearch && matchCat) {{
            c.style.display = 'block';
            visible = true;
        }} else {{
            c.style.display = 'none';
        }}
    }});

    document.getElementById('noResults').style.display = visible ? 'none' : 'block';
}}

function filterByCategory(cat, el) {{
    document.querySelectorAll('.category-tag').forEach(t => t.classList.remove('active'));
    el.classList.add('active');
    filterIdioms();
}}

// Back to top
window.addEventListener('scroll', function() {{
    document.getElementById('backToTop').classList.toggle('visible', window.scrollY > 300);
}});
</script>

</body>
</html>"""

    path = os.path.join(OUTPUT_DIR, "index.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Generated index.html")


def generate_idiom_page(idiom):
    """Generate an individual idiom detail page"""
    iid = idiom['id']
    prefix = f"idiom-{iid:02d}"

    # Previous/Next navigation
    prev_id = iid - 1 if iid > 1 else None
    next_id = iid + 1 if iid < len(IDIOMS) else None

    prev_html = f'<a href="idiom-{prev_id:02d}.html" class="nav-btn prev">← #{prev_id:02d}</a>' if prev_id else '<span class="nav-btn disabled prev">← 第一页</span>'
    next_html = f'<a href="idiom-{next_id:02d}.html" class="nav-btn next">#{next_id:02d} →</a>' if next_id else '<span class="nav-btn disabled next">最后一页 →</span>'

    # Examples HTML
    examples_html = ""
    ex_idx = 0
    for i in range(0, len(idiom['examples']), 2):
        if i+1 < len(idiom['examples']):
            speaker_a, text_a = idiom['examples'][i][0], idiom['examples'][i][1]
            text_a_cn = idiom['examples'][i][2] if len(idiom['examples'][i]) >= 3 else ''
            speaker_b, text_b = idiom['examples'][i+1][0], idiom['examples'][i+1][1]
            text_b_cn = idiom['examples'][i+1][2] if len(idiom['examples'][i+1]) >= 3 else ''

            speaker_class_a = "speaker-b" if (speaker_a == "A2") else ""
            speaker_class_b = "speaker-b" if (speaker_b == "B2" or "2" in str(speaker_b) or speaker_b in ["A2", "B2"]) else ""

            sp_a_display = "A" if speaker_a == "A2" else speaker_a
            sp_b_display = "B" if speaker_b == "B2" else speaker_b

            examples_html += f"""
            <div class="example-group">
                <div class="example-line">
                    <span class="speaker {speaker_class_a}">{sp_a_display}</span>
                    <span class="text">{text_a}</span>
                    <button class="inline-play-btn" data-audio="ex-{ex_idx}" title="朗读">▶</button>
                    <button class="trans-btn" onclick="toggleTrans(this)" title="中文译文">译</button>
                    <div class="trans-text">{text_a_cn}</div>
                </div>
                <div class="example-line">
                    <span class="speaker speaker-b">{sp_b_display}</span>
                    <span class="text">{text_b}</span>
                    <button class="inline-play-btn" data-audio="ex-{ex_idx+1}" title="朗读">▶</button>
                    <button class="trans-btn" onclick="toggleTrans(this)" title="中文译文">译</button>
                    <div class="trans-text">{text_b_cn}</div>
                </div>
            </div>
            """
            ex_idx += 2

    # Exercises HTML
    exercises_html = ""
    for ei, ex in enumerate(idiom['exercise_q']):
        exercises_html += f'<div class="exercise-item">'
        exercises_html += f'<div class="exercise-q">{ex["question"]}</div>'

        if "options" in ex:
            exercises_html += '<div class="exercise-options">'
            for oi, opt in enumerate(ex["options"]):
                opt_letter = chr(65 + oi)  # A, B, C, D
                exercises_html += f'<div class="exercise-opt" onclick="selectOption(this, \'{opt_letter}\', \'{ex["answer"][0]}\')">{opt}</div>'
            exercises_html += '</div>'
            exercises_html += f'<div class="exercise-answer" id="answer-{ei}">✅ {ex["answer"]}</div>'

        if "fill" in ex:
            fill_items = ex["fill"]
            fill_inputs_html = ""
            fill_answer_text = []
            for i, ans in enumerate(fill_items):
                fill_inputs_html += f'''
                    <input type="text" class="fill-input" id="fill-input-{ei}-{i}" placeholder="第{i+1}个空" autocomplete="off" onkeydown="if(event.key==='Enter')checkFill({ei})">
                '''
                fill_answer_text.append(ans)
            fill_answer_str = " / ".join(fill_answer_text)
            exercises_html += f'''
            <div class="fill-exercise" id="fill-{ei}">
                <div class="fill-input-row">
                    {fill_inputs_html}
                    <button class="fill-check-btn" onclick="checkFill({ei})">✓ 检查</button>
                    <button class="reveal-btn" onclick="toggleFill({ei})">👁 答案</button>
                </div>
                <div class="fill-feedback" id="fill-feedback-{ei}"></div>
                <div class="fill-answer" id="fill-answer-{ei}" style="display:none">💡 {fill_answer_str}</div>
            </div>
            '''

        exercises_html += '</div>'

    meaning_html = f"""
    <div class="meaning-item">
        <span class="label"><span class="flag-icon flag-ru">{svg_flag_ru()}</span> 意思</span>
        <span class="value">{idiom['meaning_it']}</span>
        <button class="inline-play-btn" data-audio="meaning" title="朗读">▶</button>
        <button class="trans-btn" onclick="toggleTrans(this)" title="中文译文">译</button>
        <div class="trans-text">{idiom.get('meaning_it_cn', '')}</div>
    </div>
    <div class="meaning-item">
        <span class="label"><span class="flag-icon flag-cn">{svg_flag_cn()}</span> 中文</span>
        <span class="value cn">{idiom['meaning_cn']}</span>
    </div>
    <div class="meaning-item">
        <span class="label">📖 用法</span>
        <span class="value">{idiom['usage_cn']}</span>
    </div>
    <div class="meaning-item">
        <span class="label"><span class="flag-icon flag-en">{svg_flag_en()}</span> 英语</span>
        <span class="value" style="font-style:italic;color:var(--text-mid)">{idiom['english_eq']}</span>
    </div>
    """

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>#{iid:02d} {idiom['idiom']} | 俄语习语</title>
<style>
{COMMON_CSS}
{IDIOM_PAGE_CSS}
</style>
</head>
<body>

<div class="tricolor-bar"></div>

<header class="main-header" style="padding:50px 20px 30px;">
    <h1 style="font-size:1.8rem;"><span class="flag-icon flag-ru">{svg_flag_ru()}</span> 俄语习语</h1>
    <div class="subtitle" style="font-size:0.95rem;">Русские фразеологизмы и поговорки</div>
</header>

<div class="breadcrumb">
    <a href="index.html">🏠 全部习语</a> / #{iid:02d}
</div>

<div class="idiom-container">

    <!-- Hero -->
    <div class="idiom-hero">
        <div class="idiom-number">#{iid:02d} · {idiom['category']}</div>
        <div class="idiom-text">{idiom['idiom']}</div>
        <div class="idiom-meaning-cn">{idiom['meaning_cn']}</div>
        <div class="idiom-english">{idiom['english_eq']}</div>

        <div class="audio-player">
            <button class="audio-btn" id="playBtn" onclick="togglePlay()" title="播放">▶</button>
            <div class="speed-buttons">
                <button class="speed-btn" onclick="setSpeed(0.6, this)">0.6×</button>
                <button class="speed-btn active" onclick="setSpeed(1.0, this)">1.0×</button>
                <button class="speed-btn" onclick="setSpeed(1.4, this)">1.4×</button>
            </div>
        </div>
    </div>

    <!-- Meaning -->
    <div class="section-card">
        <div class="section-header" onclick="toggleSection(this)">
            <span class="icon">📖</span> 含义 · Значение
            <span class="toggle-arrow">▼</span>
        </div>
        <div class="section-body">
            {meaning_html}
        </div>
    </div>

    <!-- Examples -->
    <div class="section-card">
        <div class="section-header" onclick="toggleSection(this)">
            <span class="icon">💬</span> 例句 · Примеры
            <span class="toggle-arrow">▼</span>
        </div>
        <div class="section-body">
            {examples_html}
        </div>
    </div>

    <!-- Cultural Note -->
    <div class="section-card">
        <div class="section-header" onclick="toggleSection(this)">
            <span class="icon">🏛️</span> 文化注释 · Культурный комментарий
            <span class="toggle-arrow">▼</span>
        </div>
        <div class="section-body">
            <div class="cultural-note">{idiom['cultural_cn']}</div>
        </div>
    </div>

    <!-- Exercises -->
    <div class="section-card">
        <div class="section-header" onclick="toggleSection(this)">
            <span class="icon">✍️</span> 练习 · Упражнения
            <span class="toggle-arrow">▼</span>
        </div>
        <div class="section-body">
            {exercises_html}
        </div>
    </div>

</div>

<!-- Navigation -->
<div class="nav-idioms">
    {prev_html}
    <a href="index.html" class="nav-btn nav-home">🏠 导航</a>
    {next_html}
</div>

<footer class="page-footer">
    <p>涛子办事处 · 俄语习语学习工具 · #{iid:02d}/{len(IDIOMS)}</p>
</footer>

<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>

<script>
// === Audio System ===
let currentAudio = null;
let currentSpeed = 1.0;
const idiomText = {json.dumps(idiom['idiom'], ensure_ascii=False)};

const audioUrl = 'audio/{safe_filename(idiom["idiom"])}.mp3';

function togglePlay() {{
    const btn = document.getElementById('playBtn');
    if (currentAudio && !currentAudio.paused) {{
        currentAudio.pause();
        btn.textContent = '▶';
        btn.classList.remove('playing');
        return;
    }}
    playIdiom(currentSpeed);
}}

function playIdiom(speed) {{
    if (currentAudio) {{
        if (currentAudio.pause) currentAudio.pause();
        if (currentAudio.src) currentAudio.src = '';
        currentAudio = null;
    }}
    currentSpeed = speed;
    document.querySelectorAll('.inline-play-btn.playing').forEach(b => b.classList.remove('playing'));
    const btn = document.getElementById('playBtn');
    btn.textContent = '⏳';
    btn.classList.remove('playing');

    const audio = new Audio(audioUrl);
    audio.preload = 'auto';
    audio.playbackRate = speed;

    function startPlay() {{
        audio.play().then(function() {{
            btn.textContent = '⏸';
            btn.classList.add('playing');
        }}).catch(function() {{
            audio.addEventListener('loadeddata', function retry() {{
                audio.play().then(function() {{
                    btn.textContent = '⏸';
                    btn.classList.add('playing');
                }}).catch(function() {{
                    btn.textContent = '▶';
                    btn.classList.remove('playing');
                }});
                audio.removeEventListener('loadeddata', retry);
            }});
        }});
    }}

    audio.addEventListener('loadeddata', startPlay, {{once: true}});
    audio.addEventListener('error', function() {{
        btn.textContent = '▶';
        btn.classList.remove('playing');
    }});
    audio.addEventListener('ended', function() {{
        btn.textContent = '▶';
        btn.classList.remove('playing');
    }});

    if (audio.readyState >= 2) {{
        startPlay();
    }}

    currentAudio = audio;
}}

function setSpeed(speed, btn) {{
    currentSpeed = speed;
    document.querySelectorAll('.speed-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    if (currentAudio && !currentAudio.paused) {{
        playIdiom(speed);
    }}
}}

// Inline text reader — each audio is an independent JSON file
function playInlineText(key, btn) {{
    if (!btn) return;

    if (btn.classList.contains('playing')) {{
        if (currentAudio) {{
            if (currentAudio.pause) currentAudio.pause();
            if (currentAudio.src) currentAudio.src = '';
        }}
        currentAudio = null;
        btn.classList.remove('playing');
        return;
    }}

    if (currentAudio) {{
        if (currentAudio.pause) currentAudio.pause();
        if (currentAudio.src) currentAudio.src = '';
        currentAudio = null;
    }}
    document.querySelectorAll('.inline-play-btn.playing').forEach(b => b.classList.remove('playing'));

    btn.classList.add('playing');

    const audioFile = 'data/idiom-{iid:02d}-audio-' + key + '.json';

    fetch(audioFile)
        .then(r => {{
            if (!r.ok) throw new Error('Not found');
            return r.json();
        }})
        .then(b64 => {{
            const audio = new Audio('data:audio/mp3;base64,' + b64);
            audio.playbackRate = currentSpeed;

            audio.onended = function() {{
                btn.classList.remove('playing');
            }};
            audio.onerror = function() {{
                btn.classList.remove('playing');
            }};

            audio.play().catch(function() {{
                btn.classList.remove('playing');
            }});
            currentAudio = audio;
        }})
        .catch(function() {{
            btn.classList.remove('playing');
        }});
}}

// Click handler for inline play buttons
document.addEventListener('click', function(e) {{
    const btn = e.target.closest('.inline-play-btn');
    if (btn && btn.dataset.audio) {{
        e.stopPropagation();
        e.preventDefault();
        playInlineText(btn.dataset.audio, btn);
    }}
}});

// Translation toggle
function toggleTrans(btn) {{
    const trans = btn.nextElementSibling;
    if (trans && trans.classList.contains('trans-text')) {{
        trans.classList.toggle('visible');
        btn.classList.toggle('active');
        btn.textContent = trans.classList.contains('visible') ? '×' : '译';
    }}
}}

// Section toggle
function toggleSection(header) {{
    header.classList.toggle('collapsed');
    const body = header.nextElementSibling;
    body.classList.toggle('collapsed');
}}

// Exercise: select option
function selectOption(el, letter, correctLetter) {{
    const parent = el.parentElement;
    const options = parent.querySelectorAll('.exercise-opt');
    const answerDiv = parent.nextElementSibling;

    options.forEach(o => o.classList.remove('selected', 'wrong', 'correct'));
    el.classList.add('selected');

    if (letter === correctLetter) {{
        el.classList.add('correct');
        answerDiv.classList.add('show');
    }} else {{
        el.classList.add('wrong');
        options.forEach(o => {{
            if (o.textContent.startsWith(correctLetter + ')')) {{
                o.classList.add('correct');
            }}
        }});
        setTimeout(() => answerDiv.classList.add('show'), 300);
    }}
}}

// Exercise: fill-in with typing input (supports multiple blanks, Cyrillic-aware)
function normalize(s) {{
    return s.toLowerCase().replace(/[^a-zа-яё\\u00C0-\\u024F]/g, '');
}}

function checkFill(id) {{
    const fb = document.getElementById('fill-feedback-' + id);
    const answerDiv = document.getElementById('fill-answer-' + id);
    const correctAnswers = answerDiv.textContent.replace('💡 ', '').trim().split(' / ');

    let allCorrect = true;
    let hasInput = false;

    for (let i = 0; i < correctAnswers.length; i++) {{
        const input = document.getElementById('fill-input-' + id + '-' + i);
        if (!input) continue;
        hasInput = true;
        const userAnswer = normalize(input.value);
        const correct = normalize(correctAnswers[i]);
        if (userAnswer === correct) {{
            input.classList.add('correct');
            input.classList.remove('wrong');
        }} else {{
            input.classList.add('wrong');
            input.classList.remove('correct');
            allCorrect = false;
        }}
    }}

    if (!hasInput) {{
        fb.className = 'fill-feedback hint';
        fb.textContent = '✏️ 请先输入你的答案';
        return;
    }}

    if (allCorrect) {{
        fb.className = 'fill-feedback correct';
        fb.textContent = '✅ 正确！';
    }} else {{
        fb.className = 'fill-feedback wrong';
        fb.textContent = '❌ 不对，再想想';
    }}
}}

function toggleFill(id) {{
    const answerDiv = document.getElementById('fill-answer-' + id);
    if (answerDiv.style.display === 'none' || answerDiv.style.display === '') {{
        answerDiv.style.display = 'block';
        const correctAnswers = answerDiv.textContent.replace('💡 ', '').trim().split(' / ');
        for (let i = 0; i < correctAnswers.length; i++) {{
            const input = document.getElementById('fill-input-' + id + '-' + i);
            if (input) {{
                input.value = correctAnswers[i].trim();
                input.classList.add('correct');
                input.classList.remove('wrong');
            }}
        }}
        document.getElementById('fill-feedback-' + id).className = 'fill-feedback correct';
        document.getElementById('fill-feedback-' + id).textContent = '✅ 答案已填入';
    }} else {{
        answerDiv.style.display = 'none';
    }}
}}

// Back to top
window.addEventListener('scroll', function() {{
    document.getElementById('backToTop').classList.toggle('visible', window.scrollY > 300);
}});
</script>

</body>
</html>"""

    path = os.path.join(OUTPUT_DIR, f"{prefix}.html")
    with open(path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"✓ Generated {prefix}.html - {idiom['idiom']}")


def generate_all():
    """Generate all files"""
    print("=" * 60)
    print("Russian Idioms HTML Generator")
    print("=" * 60)

    print("\nGenerating main idiom audio files...")
    generate_audio_files()

    audio_cache = generate_inline_audio_files()
    build_inline_audio_json(audio_cache)

    print("\nGenerating HTML pages...")
    generate_index_html()
    for idiom in IDIOMS:
        generate_idiom_page(idiom)

    print(f"\n✓ Generated {len(IDIOMS)} idiom pages + index.html")
    print(f"✓ Generated {len(audio_cache)} inline audio clips in data/")
    print(f"Total: {len(IDIOMS) + 1} HTML files")
    print("\nAll done! Open index.html to start.")


if __name__ == "__main__":
    generate_all()
