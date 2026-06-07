FROM public.ecr.aws/docker/library/node:20-alpine

WORKDIR /app

COPY app/package.json .
RUN npm install --omit=dev

COPY app/ .

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000

CMD ["npm", "start"]
