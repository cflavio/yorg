#version 130
in vec2 texcoord;
uniform sampler2D input_tex;
out vec4 p3d_FragColor;
const vec3 lum = vec3(.2126, .7152, .0722);

float luminance(vec3 col) { return dot(lum, col); }

vec4 sobel() {
    ivec2 pix = ivec2(gl_FragCoord.xy);
    float s00 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(-1, 1)).rgb);
    float s10 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(-1, 0)).rgb);
    float s20 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(-1, -1)).rgb);
    float s01 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(0, 1)).rgb);
    float s21 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(0, -1)).rgb);
    float s02 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(1, 1)).rgb);
    float s12 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(1, 0)).rgb);
    float s22 = luminance(texelFetchOffset(input_tex, pix, 0, ivec2(1, -1)).rgb);
    float sx = s00 + 2 * s10 + s20 - (s02 + 2 * s12 + s22);
    float sy = s00 + 2 * s01 + s02 - (s20 + 2 * s21 + s22);
    float g = sx * sx + sy * sy;
    return mix(vec4(1), vec4(0, 0, 0, 1), smoothstep(.01, 1, g));
}

void main() {
    p3d_FragColor = sobel() * texture(input_tex, texcoord);
}
