#version 130
in vec4 texcoord;
out vec4 p3d_FragColor;

void main() {
    p3d_FragColor = vec4(vec3((texcoord.z / texcoord.w) * .5 + .5), 1);
}