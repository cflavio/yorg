#version 130
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec2 p3d_MultiTexCoord0;
out vec3 pos;
out vec3 normal;
out vec2 texcoord;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main() {
    texcoord = p3d_MultiTexCoord0;
    normal = normalize(p3d_NormalMatrix * p3d_Normal);
    pos = vec3(p3d_ModelViewMatrix * p3d_Vertex);
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
