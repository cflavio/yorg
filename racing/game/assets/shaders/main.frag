#version 130
in vec2 texcoord;
in vec4 lightclip;
in vec4 shadowcoord;
in vec3 pos;
in vec3 normal;
out vec4 p3d_FragColor;
uniform sampler2D p3d_Texture0;
uniform sampler2DShadow depthmap;
uniform vec4 ambient;
uniform int num_lights;
const int toon_levels = 4;
const float toon_scale_factor = 1.0 / toon_levels;

struct lgt_info {
  vec4 pos; // in eye coords
  vec3 amb;
  vec3 diff;
  vec3 spec;
  vec3 dir; // normalized direction of the spotlight
  float exp; // angular attenuation exponent
  float cutoff; // cutoff angle (between 0 and 90)
};

uniform lgt_info lights[<LIGHTS>];

uniform struct {
    vec4 ambient;
    vec4 diffuse;
    vec3 specular;
    float shininess;
} p3d_Material;

float smoothfloor(float v) {
  float cv = ceil(v);
  return floor(v) + smoothstep(cv - .15, cv, v);
}

float toon_val(float v) {
  // return v;  // phong model
  return smoothfloor(v * toon_levels) * toon_scale_factor;
}

void toon(int lgt_idx, out vec3 amb_diff, out vec3 spec) {
  lgt_info lgt = lights[lgt_idx];
  amb_diff = vec3(0);
  spec = vec3(0);
  if (lgt.amb != vec3(0)) { // ambient light
    amb_diff = lgt.amb * vec3(p3d_Material.ambient);
    return;
  }
  vec3 s = normalize(lgt.pos.xyz - pos * lgt.pos.w);
  vec3 v = normalize(-pos.xyz);
  vec3 h = normalize(v + s);
  vec3 n = normalize(normal);
  float s_dot_n = max(dot(s, n), .0);
  amb_diff = lgt.diff * vec3(p3d_Material.diffuse) * toon_val(s_dot_n);
  vec3 ks = p3d_Material.specular;
  float spec_factor = pow(max(dot(h, n), .0), p3d_Material.shininess);
  spec = lgt.spec * ks * toon_val(spec_factor);
  spec *= step(.0, s_dot_n);
  if (lgt.exp == .0) // point light or directional, not a spotlight
    return;
  float ang = acos(dot(-s, lgt.dir));
  float cutoff = radians(clamp(lgt.cutoff, 0, 90));
  float spot_factor =  toon_val(pow(dot(-s, lgt.dir), lgt.exp)) * step(ang, cutoff);
  amb_diff *= spot_factor;
  spec *= spot_factor;
}

float saturate(float v) { return clamp(v,0.0,1.0); }

vec4 vsaturate(vec4 v) {
  return vec4(clamp(v[0],0.0,1.0), clamp(v[1],0.0,1.0),
              clamp(v[2],0.0,1.0), clamp(v[3],0.0,1.0));
}

void main() {
    vec3 amb_diff = vec3(.0);
    vec3 spec = vec3(.0);
    vec3 _amb_diff;
    vec3 _spec;
    vec4 tex_col = texture(p3d_Texture0, texcoord);
    for (int i=0; i < num_lights; i++) {
        toon(i, _amb_diff, _spec);
        amb_diff += _amb_diff;
        spec += _spec;
    }
    vec3 circleoffs = vec3(lightclip.xy / lightclip.w, 0);
    float falloff = saturate(1.0 - dot(circleoffs, circleoffs));
    vec4 col = vsaturate(vec4(amb_diff, 1) * tex_col + vec4(spec, 1));
    float shade = min(.4 + shadow2DProj(depthmap, shadowcoord).r, 1);
    p3d_FragColor = col * (((1 - falloff) + falloff * shade));
}