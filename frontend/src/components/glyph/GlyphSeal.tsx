import { useEffect, useState } from 'react'
import './GlyphSeal.css'

interface GlyphSealProps {
  score: number
  level: 'alpha' | 'beta' | 'gamma'
  animated?: boolean
  size?: number
}

export function GlyphSeal({ score, level, animated = true, size = 200 }: GlyphSealProps) {
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    if (animated) {
      setIsAnimating(true)
    }
  }, [animated])

  const getLevelColor = () => {
    switch (level) {
      case 'gamma': return '#10b981'
      case 'beta': return '#3b82f6'
      case 'alpha': return '#f59e0b'
      default: return '#6b7280'
    }
  }

  // 六芒星のパス（2つの正三角形を重ねる）
  const hexagramPath = () => {
    const centerX = size / 2
    const centerY = size / 2
    const radius = size * 0.4

    // 上向き三角形
    const triangle1 = [
      [centerX, centerY - radius],
      [centerX + radius * Math.cos(Math.PI / 6), centerY + radius * Math.sin(Math.PI / 6)],
      [centerX - radius * Math.cos(Math.PI / 6), centerY + radius * Math.sin(Math.PI / 6)]
    ]

    // 下向き三角形
    const triangle2 = [
      [centerX, centerY + radius],
      [centerX - radius * Math.cos(Math.PI / 6), centerY - radius * Math.sin(Math.PI / 6)],
      [centerX + radius * Math.cos(Math.PI / 6), centerY - radius * Math.sin(Math.PI / 6)]
    ]

    const path1 = 'M ' + triangle1.map(p => p.join(',')).join(' L ') + ' Z'
    const path2 = 'M ' + triangle2.map(p => p.join(',')).join(' L ') + ' Z'

    return { path1, path2 }
  }

  const { path1, path2 } = hexagramPath()
  const color = getLevelColor()

  return (
    <div className={'glyph-seal' + (isAnimating ? ' animating' : '')}>
      <svg
        width={size}
        height={size}
        viewBox={'0 0 ' + size + ' ' + size}
        className="glyph-svg"
      >
        {/* 外側の円環 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size * 0.45}
          fill="none"
          stroke={color}
          strokeWidth="2"
          opacity="0.3"
          className="glyph-outer-ring"
        />

        {/* 内側の円環 */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={size * 0.35}
          fill="none"
          stroke={color}
          strokeWidth="1"
          opacity="0.2"
          className="glyph-inner-ring"
        />

        {/* 六芒星 - 上向き三角形 */}
        <path
          d={path1}
          fill={color}
          opacity="0.2"
          className="glyph-triangle-1"
        />

        {/* 六芒星 - 下向き三角形 */}
        <path
          d={path2}
          fill={color}
          opacity="0.2"
          className="glyph-triangle-2"
        />

        {/* 六芒星の輪郭 */}
        <path
          d={path1}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="glyph-triangle-outline-1"
        />
        <path
          d={path2}
          fill="none"
          stroke={color}
          strokeWidth="2"
          className="glyph-triangle-outline-2"
        />

        {/* 中央のスコア */}
        <text
          x={size / 2}
          y={size / 2}
          textAnchor="middle"
          dominantBaseline="central"
          className="glyph-score"
          fill={color}
          fontSize={size * 0.2}
          fontWeight="bold"
        >
          {score}
        </text>

        {/* 放射状のパーティクル */}
        {[0, 1, 2, 3, 4, 5].map((i) => (
          <circle
            key={i}
            cx={size / 2}
            cy={size / 2}
            r="3"
            fill={color}
            className={'glyph-particle glyph-particle-' + i}
            style={{
              transformOrigin: size / 2 + 'px ' + size / 2 + 'px'
            }}
          />
        ))}
      </svg>

      {isAnimating && (
        <div className="glyph-stamp-effect">
          <div className="glyph-stamp-circle" style={{ borderColor: color }} />
          <div className="glyph-stamp-circle" style={{ borderColor: color }} />
          <div className="glyph-stamp-circle" style={{ borderColor: color }} />
        </div>
      )}
    </div>
  )
}
