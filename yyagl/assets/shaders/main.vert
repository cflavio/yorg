#version 130
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoord;
out vec4 shadowcoord;
out vec4 lightclip;
out vec3 pos;
out vec3 normal;
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform vec4 mspos_light;
uniform mat4 trans_model_to_clip_of_light;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

float saturate(float v) { return clamp(v,0.0,1.0); }

void main() {
    vec4 _pos = p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
    vec4 pushed = _pos + vec4(p3d_Normal * .8, 0);
    lightclip = trans_model_to_clip_of_light * pushed;
    shadowcoord = lightclip * vec4(.5, .5, .5, 1) +
                  lightclip.w * vec4(.5, .5, .5, 0);
    normal = normalize(p3d_NormalMatrix * p3d_Normal);
    pos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    gl_Position = p3d_ModelViewProjectionMatrix  * _pos;
}