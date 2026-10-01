# Shader-Side Morphing Pattern

The correct way to morph particle positions in R3F without per-frame BufferAttribute updates (which cause GPU stalls and lint errors).

## The Anti-Pattern (DON'T DO THIS)

```tsx
// ❌ BAD: Forces GPU→CPU sync every frame
const posAttr = useMemo(() => new THREE.BufferAttribute(idlePositions.slice(), 3), [idlePositions]);
const targetAAttr = useMemo(() => new THREE.BufferAttribute(digit3.slice(), 3), [digit3]);
const targetBAttr = useMemo(() => new THREE.BufferAttribute(digit2.slice(), 3), [digit2]);

useFrame(() => {
  // This triggers ReadPixels and GPU stalls
  targetAAttr.array.set(newPositions);
  targetAAttr.needsUpdate = true;
  targetBAttr.array.set(nextPositions);
  targetBAttr.needsUpdate = true;
  uniforms.uMorphProgress.value = progress;
});
```

**Symptoms:** `GL Driver Message: GPU stall due to ReadPixels`, ESLint `react-hooks/immutability` errors, 60fps drops.

## The Correct Pattern: Shader-Side Morph

### Vertex Shader (handles all morphing on GPU)

```glsl
// vertexShader
uniform float uTime;
uniform float uProgress;      // 0→1 morph progress
uniform int uPhase;           // which target: 1=3, 2=2, 3=1, 4=scatter
uniform vec2 uMouse;
uniform float uMouseActive;

attribute vec3 positionIdle;
attribute vec3 position3;
attribute vec3 position2;
attribute vec3 position1;
attribute vec3 positionScatter;

varying float vAlpha;

vec3 getTarget() {
  if (uPhase == 1) return position3;
  else if (uPhase == 2) return position2;
  else if (uPhase == 3) return position1;
  else if (uPhase == 4) return positionScatter;
  return positionIdle;
}

void main() {
  vec3 target = getTarget();
  vec3 pos = mix(positionIdle, target, uProgress);

  // Mouse interaction in world space
  vec2 mouseWorld = uMouse;
  float dist = distance(pos.xy, mouseWorld);
  float mouseRadius = 1.8;
  float mouseForce = smoothstep(mouseRadius, 0.0, dist) * 2.0 * uMouseActive;
  vec2 dir = normalize(pos.xy - mouseWorld + 0.001);
  pos.xy += dir * mouseForce;

  // Subtle Z wobble
  pos.z += sin(pos.x * 2.0 + uTime * 0.5) * 0.03;

  vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
  float sizeAttenuation = 300.0 / -mvPosition.z;
  gl_PointSize = max(1.0, sizeAttenuation * 0.8);
  gl_Position = projectionMatrix * mvPosition;

  vAlpha = 1.0 - smoothstep(0.0, 1.0, uProgress) * 0.3;
}
```

### Fragment Shader

```glsl
// fragmentShader
uniform vec3 uColor;
varying float vAlpha;

void main() {
  float d = length(gl_PointCoord - vec2(0.5));
  if (d > 0.5) discard;
  float alpha = smoothstep(0.5, 0.1, d) * vAlpha;
  gl_FragColor = vec4(uColor, alpha * 0.9);
}
```

### Component: Pass All Targets as Attributes

```tsx
function ParticlePoints({
  uniforms,
  positionIdle,
  position3,
  position2,
  position1,
  positionScatter,
  onComplete,
}: {
  uniforms: Uniforms;
  positionIdle: Float32Array;
  position3: Float32Array;
  position2: Float32Array;
  position1: Float32Array;
  positionScatter: Float32Array;
  onComplete: () => void;
}) {
  const { camera } = useThree();
  const startTime = useRef(0);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const onPointerMove = useCallback(
    (e: React.PointerEvent<THREE.Points>) => {
      const rect = (e.target as HTMLCanvasElement).getBoundingClientRect();
      const x = ((e.nativeEvent.clientX - rect.left) / rect.width) * 2 - 1;
      const y = -((e.nativeEvent.clientY - rect.top) / rect.height) * 2 + 1;
      const vec = new THREE.Vector3(x, y, 0.5);
      vec.unproject(camera);
      const dir = vec.sub(camera.position).normalize();
      const distance = -camera.position.z / dir.z;
      const pos = camera.position.clone().add(dir.multiplyScalar(distance));
      uniforms.uMouse.value.set(pos.x, pos.y);
      uniforms.uMouseActive.value = 1;
    },
    [camera, uniforms]
  );

  // eslint-disable-next-line react-hooks/exhaustive-deps -- R3F useFrame intentionally mutates uniforms
  useFrame(({ clock }) => {
    if (startTime.current === 0) startTime.current = clock.getElapsedTime();

    const t = clock.getElapsedTime() - startTime.current;
    uniforms.uTime.value = t;

    let phase = 0;
    let progress = 0;
    const phaseDurations = [1.5, 1.5, 1.5, 2.0];
    const phaseNames = [1, 2, 3, 4];

    let elapsed = 0;
    for (let i = 0; i < phaseDurations.length; i++) {
      if (t < elapsed + phaseDurations[i]) {
        phase = phaseNames[i];
        progress = Math.min((t - elapsed) / 0.8, 1);
        break;
      }
      elapsed += phaseDurations[i];
    }

    if (t >= elapsed) {
      phase = 4;
      progress = Math.min((t - elapsed) / 1.0, 1);
    }

    uniforms.uPhase.value = phase;
    uniforms.uProgress.value = progress;

    if (phase === 4 && progress >= 1) {
      uniforms.uColor.value.lerp(new THREE.Color("#ff4d00"), 0.02);
    } else {
      uniforms.uColor.value.set("#f1efe8");
    }

    if (t > 6.5) {
      onCompleteRef.current();
    }
  });

  return (
    <points onPointerMove={onPointerMove}>
      <bufferGeometry>
        <bufferAttribute attach="attributes-positionIdle" args={[positionIdle, 3]} />
        <bufferAttribute attach="attributes-position3" args={[position3, 3]} />
        <bufferAttribute attach="attributes-position2" args={[position2, 3]} />
        <bufferAttribute attach="attributes-position1" args={[position1, 3]} />
        <bufferAttribute attach="attributes-positionScatter" args={[positionScatter, 3]} />
      </bufferGeometry>
      <shaderMaterial
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
```

### Parent Component: Precompute Positions Once

```tsx
export default function HeroCanvas({ onComplete }: { onComplete: () => void }) {
  const [ready, setReady] = useState(false);
  const [positions, setPositions] = useState<{
    idle: Float32Array;
    d3: Float32Array;
    d2: Float32Array;
    d1: Float32Array;
    scatter: Float32Array;
  } | null>(null);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uProgress: { value: 0 },
    uPhase: { value: 0 },
    uMouse: { value: new THREE.Vector2(0, 0) },
    uMouseActive: { value: 0 },
    uColor: { value: new THREE.Color("#f1efe8") },
  }), []);

  useEffect(() => {
    setPositions({
      idle: generateIdlePositions(),
      d3: generateDigitPositions("3"),
      d2: generateDigitPositions("2"),
      d1: generateDigitPositions("1"),
      scatter: generateScatterPositions(),
    });
    setTimeout(() => setReady(true), 0); // avoid sync setState warning
  }, []);

  if (!ready || !positions) {
    return (
      <Canvas camera={{ position: [0, 0, 5], fov: 60 }} dpr={[1, 1.5]}>
        <color attach="background" args={["#0a0a0a"]} />
      </Canvas>
    );
  }

  const { idle, d3, d2, d1, scatter } = positions;

  return (
    <Canvas camera={{ position: [0, 0, 5], fov: 60 }} dpr={[1, 1.5]}>
      <ParticlePoints
        uniforms={uniforms}
        positionIdle={idle}
        position3={d3}
        position2={d2}
        position1={d1}
        positionScatter={scatter}
        onComplete={onComplete}
      />
    </Canvas>
  );
}
```

## Key Principles

| Principle | Why |
|-----------|-----|
| Precompute all positions in `useEffect` | Zero per-frame JS work |
| Pass 5 target attributes to shader | GPU handles all morphing |
| Single `uProgress` + `uPhase` uniforms | Minimal uniform updates |
| `useFrame` only updates uniforms | No BufferAttribute.array.set() |
| Mouse unproject in world space | Correct 3D interaction |

## Timing Phases (Total ~6.5s)

| Phase | Duration | Morph Time | Target |
|-------|----------|------------|--------|
| idle → "3" | 1.5s | 0.8s | digit "3" |
| "3" → "2" | 1.5s | 0.8s | digit "2" |
| "2" → "1" | 1.5s | 0.8s | digit "1" |
| "1" → scatter | 2.0s | 1.0s | random cloud |
| → headline | 0.3s | flash | text reveal |